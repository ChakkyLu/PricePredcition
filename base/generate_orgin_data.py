import os
import time

from .preprocessing_newsdata import *
from .news_grabber import grabber_newsbitcoin, grabber_ccn
from .price_grabber import get_poloniex_data
from collections import defaultdict
from .csv_operation import read_to_dict, write_to_csv, write_test_data


def percentage_change(percentage):
    change = round(percentage, 1)
    return change


def altitude_word(processed_titles, change):
    title_classifier_dict = defaultdict(list)
    title_word_dict = {}
    for i, title in enumerate(processed_titles):
        for word in title:
            title_classifier_dict[word].append(change[i])
    for key, value in title_classifier_dict.items():
        title_word_dict[key] = len(value)
    return title_word_dict


#----------------For train-----------------
    # time_period: classify news every 60*time_period seconds
    # mode: {
    #     0: from news.bitcoin.com
    #     1: from ccn.com
    # }
    # extraClass:{
    #     true: up, down, same three classes
    #     false: up or down
    # }
#-------------------------------------------

def get_origin_data(time_period, mode, extraClass=False):
    datapath = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data'
    if mode == 0:
        titles, update_time = grabber_newsbitcoin(500, 0)
    if mode == 1:
        titles, update_time = grabber_ccn(500, 0)
    processed_titles, processed_time = preprocessing_newsdata(
        titles, update_time, mode)
    news_data = {}

    for i in range(len(processed_time)):
        news_data[i] = {'time': processed_time[i], 'news': titles[i]}
    write_to_csv(news_data, datapath+"/backup.csv", ['time', 'news'])

    print("==========Grab News Finish=========")
    btc_chart_data = get_poloniex_data('USDT_BTC', time_period*60, 1506816000)
    btc_chart_data.set_index('date', inplace=True)
    percentage_changes = []
    round_up_percentage_changes = []
    flag_change = []

    for time in processed_time:
        now = btc_chart_data.iloc[
            btc_chart_data.index.get_loc(time, method='nearest')]['close']

        after = btc_chart_data.iloc[
            btc_chart_data.index.
                get_loc(time, method='nearest')+time_period]['close']

        price_change = (after - now) / now * 100

        percentage_changes.append(price_change)
        round_up_percentage_changes.append(percentage_change(price_change))
        if not extraClass:
            flag_change.append(1) if price_change > 0.0 else flag_change.append(0)
        else:
            if price_change == 0.0: flag_change.append(0)
            if price_change > 0.0: flag_change.append(1)
            else:   flag_change.append(-1)

    origin_news_tag = {}

    for i in range(len(processed_titles)):
        origin_news_tag[i] = {flag_change[i]: processed_titles[i]}
    write_to_csv(origin_news_tag, datapath+"/origin_news_data.csv", ['flag', 'news'])
    print("==========Obtain Original Data Finish=========")

    # -------------altitude word: deprecated now---------------
    flag_classifier_dict = altitude_word(processed_titles, flag_change)
    write_to_csv(flag_classifier_dict, datapath+"/word_message.csv", ['word', 'message'])


def change_interval_influence():
    time_period = 12*60*60
    datapath = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data'
    dicts = read_to_dict(datapath+'/backup.csv')
    previous_news = read_to_dict(datapath+'/origin_news_data.csv')
    update_time, titles= [], []
    for key, value in dicts.items():
        value = eval(value)
        update_time.append(value['time'])
    for key, value in previous_news.items():
        value = eval(value)
        if 0 in titles:
            titles.append(value[0])
        else:
            titles.append(value[1])

    # update_time = update_time[6:]
    # titles = titles[60:]

    print("=========Get previous data ok==========")
    btc_chart_data = get_poloniex_data('USDT_BTC', 300, 1486710058)
    btc_chart_data.set_index('date', inplace=True)
    percentage_changes = []
    round_up_percentage_changes = []
    flag_change = []

    for time in update_time:
        if time < 1506816000: continue
        now = btc_chart_data.iloc[
            btc_chart_data.index.get_loc(time, method='nearest')]['close']

        after = btc_chart_data.iloc[
            btc_chart_data.index.
                get_loc(time+time_period, method='nearest')]['close']

        price_change = (after - now) / now * 100

        percentage_changes.append(price_change)
        round_up_percentage_changes.append(percentage_change(price_change))
        flag_change.append(1) if price_change > 0.0 else flag_change.append(0)
        print(flag_change[-1])

    origin_news_tag = {}

    for i in range(len(flag_change)):
        origin_news_tag[i] = {flag_change[i]: titles[i]}
    write_to_csv(origin_news_tag, datapath + "/train_data/origin_news_data_12.csv", ['flag', 'news'])
    print("==========Obtain Original Data Finish=========")

def get_current_news(time_period, mode):
    cur_time = int(time.time())
    step_time = time_period*60
    if mode == 0:
        titles, update_time = grabber_newsbitcoin(10, 1)
    if mode == 1:
        titles, update_time = grabber_ccn(10, 1)
    processed_titles, _ = preprocessing_newsdata(
        titles, update_time, mode)
    print("==========Grab Current News Finish=========")
    btc_chart_data = get_poloniex_data('USDT_BTC', 300, cur_time-step_time)
    btc_chart_data.set_index('date', inplace=True)
    prices = {}
    end_time = cur_time
    count = 20
    while count:
        price = btc_chart_data.iloc[
            btc_chart_data.index.get_loc(end_time, method='nearest')]['high']
        prices[end_time] = price
        end_time -= step_time
        count -= 1
    print("======Grab previous price OK======")

    cur_news = {}
    for i in range(len(processed_titles)):
        cur_news[i] = processed_titles[i]

    datapath = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data'
    write_to_csv(cur_news, datapath+"/current_news.csv", ['num', 'news'])
    write_to_csv(prices, datapath+"/previous_price.csv", ['date', 'price'])


def get_test_news(time_period, mode, extraClass=False):
    import time
    cur_time = int(time.time())
    end_time = cur_time
    step_time = time_period*60

    if mode == 0:
        titles, update_time = grabber_newsbitcoin(10, 0)
    if mode == 1:
        titles, update_time = grabber_ccn(40, 0)
    print("============Grab test news ok==========")
    processed_titles, processed_time = preprocessing_newsdata(
        titles, update_time, mode)
    early_time = processed_time[-1]
    print("==========Process test News OK=========")

    btc_chart_data = get_poloniex_data('USDT_BTC', time_period*60, early_time)
    btc_chart_data.set_index('date', inplace=True)
    percentage_changes = []
    round_up_percentage_changes = []
    flag_change = []

    step_time = 1*60*60

    for time in processed_time:
        now = btc_chart_data.iloc[
            btc_chart_data.index.get_loc(time, method='nearest')]['close']

        after = btc_chart_data.iloc[
            btc_chart_data.index.
                get_loc(time, method='nearest') + time_period]['close']

        price_change = (after - now) / now * 100

        percentage_changes.append(price_change)
        round_up_percentage_changes.append(percentage_change(price_change))
        if not extraClass:
            flag_change.append(1) if price_change > 0.0 else flag_change.append(0)
        else:
            if price_change == 0.0: flag_change.append(0)
            if price_change > 0.0: flag_change.append(1)
            else:   flag_change.append(-1)

    prices = {}
    # count = 20
    # while count:
    #     price = btc_chart_data.iloc[
    #         btc_chart_data.index.get_loc(end_time, method='nearest')]['high']
    #     prices[end_time] = price
    #     end_time -= step_time
    #     count -= 1
    # print("======Grab previous price OK======")

    origin_news_tag = {}

    for i in range(len(processed_titles)):
        origin_news_tag[i] = {flag_change[i]: processed_titles[i]}
    datapath = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/data/test_data/'
    write_to_csv(origin_news_tag, datapath+"test_news.csv", ['flag', 'news'])
    # write_to_csv(prices, datapath + "/previous_price.csv", ['date', 'price'])

    print("==========Obtain test Data Finish=========")

