from naiveBayes import test_bayes
import sys
sys.path.append("..")
from prediction.naiveBayes import BayesModel as BayesModel
from prediction.LSTM import lstmModel as lstmModel
from base.generate_orgin_data import *
from LSTM import *

if __name__ == "__main__":
    # get_origin_data(5, 0)
    change_interval_influence()
    # test_bayes()
    # getBitcoin(1)
    # lstm()
    # up_down_test()
    # test_bayes()
    # get_test_news(5, 1)