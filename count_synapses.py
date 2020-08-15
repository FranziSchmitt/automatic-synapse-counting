from app.app import App
from data_io.data_loading import DataLoader
from synapse_counting.synapse_counter import SynapseCounter

if __name__=='__main__':
    app = App()
    dl = DataLoader()
    sc = SynapseCounter()