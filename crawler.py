import sys
from multiprocessing import Process, Queue, cpu_count, JoinableQueue, Semaphore, Manager

import requests
import requests_html
from fake_useragent import UserAgent
import bs4

url = "https://bscscan.com/tokentxns"
get_txns_page_url = lambda page_num: f"https://bscscan.com/tokentxns?p={page_num}"
get_contract_url = lambda address: f"https://bscscan.com/token/{address}"
DEAULT_RECURSION_LIMIT = sys.getrecursionlimit()


def setRecursionLimit(limit=DEAULT_RECURSION_LIMIT):
    sys.setrecursionlimit(limit)


class E_token:
    _icon = "/images/main/empty-token.png"

    @classmethod
    def new(cls, txn_token):
        return cls().build(txn_token)

    def build(self, txn_token):
        tmp = txn_token.select_one("img").attrs
        self.icon = tmp.get("src", -1)

        if self.icon == -1:
            self.icon = tmp["data-cfsrc"]

        if self.icon != E_token._icon:
            return None

        self.ad_contract = txn_token.select_one("a").attrs["href"].lstrip(
            "/token/")
        self.name = txn_token.select_one("a").text.strip()

        if self.name.find("...") != -1:
            names = txn_token.findAll("span")
            for name in names:
                self.name = self.name.replace(name.font.text, name["title"])

        return self

    def __repr__(self):
        return f"<{self.name} {self.ad_contract}>"


class E_Transaction():
    @classmethod
    def new(cls, txn_object):
        return cls().build(txn_object)

    def build(self, txn_object):
        self.txn_token = E_token().new(
            txn_object.select_one("td:nth-child(9)"))
        if self.txn_token == None: return None

        self.txn_hash = txn_object.select_one("td:nth-child(2)").text
        self.txn_age = txn_object.select_one("td:nth-child(3)").text

        self.txn_from = txn_object.select_one("td:nth-child(5)").text
        self.txn_to = txn_object.select_one("td:nth-child(7)").text

        self.txn_value = txn_object.select_one("td:nth-child(8)").text

        return self

    def __repr__(self):
        return f"<{self.txn_hash} {self.txn_token}>"


def get_request_using_requests_html(url):
    r = None
    with requests_html.HTMLSession() as session:
        r = session.get(url)
    return r


def get_request_using_requests(url):
    r = requests.get(url, headers={'User-Agent': UserAgent().chrome})
    return r


def produce_txns(url, using="requests"):
    get_request = get_request_using_requests
    if using == "requests_html":
        get_request = get_request_using_requests_html

    resp = bs4.BeautifulSoup(get_request(url).text, 'html.parser')
    txns = resp.select('tbody > tr')
    return txns


def url_server(URL_q, NP, pages=20):
    for i in range(pages):
        URL_q.put(get_txns_page_url(i))

    for i in range(NP):
        URL_q.put("END")


def crawler(RESP_q, URL_q, SEM, using):
    with SEM:
        while True:
            url = URL_q.get()

            if url == "END":
                break

            try:
                RESP = produce_txns(url, using)
            except Exception:
                print("Encountered Error")
                continue
            RESP_q.put(RESP)


def preprocess(RESP_q, RES_q, SEM, NP):
    while SEM.get_value() < NP or not RESP_q.empty():
        try:
            resp = RESP_q.get(timeout=0.5)
        except Exception:
            continue

        for txn in resp:
            try:
                _txn = E_Transaction().new(txn)
            except KeyError:
                print("Encountered KeyError")
                continue
            if _txn != None:
                RES_q.append(_txn)

        RESP_q.task_done()


class Res_Manager:
    def __init__(self, RES_q, pages, using):
        self.pages = pages
        self.URL_q = Queue()
        self.RESP_q = JoinableQueue()
        self.crawler_processes = 6  #* 8 CPU system
        self.preprocess_processes = 2
        self.SEM = Semaphore(self.crawler_processes)
        self.RES_q = RES_q
        self.using = using

    def start(self):
        self.worker = []

        for i in range(0, self.crawler_processes):
            self.worker.append(
                Process(target=crawler,
                        args=(self.RESP_q, self.URL_q, self.SEM, self.using)))

        for i in range(0, self.preprocess_processes):
            self.worker.append(
                Process(target=preprocess,
                        args=(self.RESP_q, self.RES_q, self.SEM,
                              self.crawler_processes)))

        url_server(self.URL_q, self.crawler_processes, self.pages)

        for worker in self.worker:
            worker.start()

        self.stop()

    def stop(self):
        for worker in self.worker:
            worker.join()

        try:
            while self.RESP_q.get_nowait():
                self.RESP_q.task_done()
        except Exception:
            pass

        self.RESP_q.join()
        self.RESP_q.close()
        self.URL_q.close()


def get_txns_parallel(pages=20, using="requests"):
    setRecursionLimit(15000)
    res = None
    with Manager() as manager:
        data = manager.list()
        Res_Manager(data, pages, using).start()
        res = list(data)
    return res


def get_txns_serial(pages=20, using="requests"):
    res = []
    for i in range(pages):
        url = get_txns_page_url(i)
        resp = produce_txns(url, using)
        for txn in resp:
            _txn = E_Transaction().new(txn)
            if _txn != None:
                res.append(_txn)
    return res
