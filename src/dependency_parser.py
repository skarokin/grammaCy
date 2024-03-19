# 1. able to train dependency parser on data from ../data/processed
# 2. able to use trained model from ../data/models to parse input sentences
class DependencyParser:
    def __init__(self, model_path):
        pass

    def train(self, processed_data_path, path_to_save):
        '''
        train dependency parser on processed data; save model to model_path
        '''
        pass

    def parse(self, input_sentence, model_path):
        '''
        parse input sentence into a tree; by default uses pretrained model
        '''
        pass

def test_dependency_parser():
    pass