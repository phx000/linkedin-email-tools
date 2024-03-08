import utils
import strategies
from tools import manual


def main():
    project = utils.dict_query("select * from projects where name='pa'")[0]
    strategies.default_strategy(project)

manual.add_from_txt_file("C:/Users/Philip/Downloads/addresses_txt.txt","pa")
# main()
