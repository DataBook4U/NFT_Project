#Used Libraries:
import re
import numpy as np
import pandas as pd
import praw
import json
import requests
import matplotlib.pyplot as plt
import urllib
from urllib.request import Request, urlopen
import snscrape.modules.twitter as sntwitter
from bs4 import BeautifulSoup as bs
from requests import get


###Ouptut Modification For Pycharm###
desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',20)
######################################



###################### Scrapping - Social Media #################################################################

#Class for RedditScrapping
class ScrapeReddit:
    def __init__(self, user_agent, client_id, client_secret):
        self.user_agent= user_agent
        self.client_id = client_id
        self.client_secret = client_secret


        self.redit = praw.Reddit(
            client_id = self.client_id,
            client_secret = self.client_secret,
            user_agent = self.user_agent)


    def FindTopics(self):
        headlines = set()
        ids = set()
        creator = set()
        for submission in self.redit.subreddit("NFT").top(limit=None):

            headlines.add(submission.title)
            ids.add(submission.id)
            creator.add(submission.author)
            #.add(submission.created_utc)
            #.add(submission.score)
            #.add(submission.upvote_ratio)
            #.add(submission.url)


        df_headlines = pd.DataFrame(list(headlines) , columns=['Headlines:'])
        df_ids = pd.DataFrame(list(ids), columns=['IDs:'])
        df_author = pd.DataFrame(list(creator), columns=['Creator:'])

        df_comb = pd.concat([df_headlines, df_ids, df_author], axis=0)

        return df_comb

"""""
r1_input = ScrapeReddit("Scraper 1.0 by u/ExoticTrack-200", 'hzOgEEsCkTaBb1gHTVkpsw', 'grDAf4hLL7slDn2-9cN32F6JcdxOuA')
r1 = r1_input.FindTopics()

print(r1)

"""

############################## Scrapping Etherium Blockchain from Ehterscan#############################################

#Class to get Log data of a specific NFT, needs the NFT Contract Address to work!
class nft_log_data:
    def __int__(self, ContractAddress: str):
        self.url = 'https://api.etherscan.io/api'
        self.params = {
            'module': 'logs',
            'action': 'getLogs',
            'address': ContractAddress,
            'apikey': "K3XB7RJNEGRD8GGK42UDBCQQN4HUMB483H"
            }

        r = requests.get(self.url, params=self.params)
        json_data = json.loads(r.text)["result"]
        df = pd.json_normalize(json_data)
        #df[["topics", "data", "timeStamp", "transactionHash", ]].head()

        return df

#class to get nft transaction data
#transaction details of a specific Collection like the "Bored Ape Yacht Club"

class nft_transaction_data:
    def __int__(self, ContractAddress: str):
        self.url = 'https://api.etherscan.io/api'
        self.params = {
            'module': 'account',
            'action': 'txlist',
            'address': ContractAddress,
            'apikey': "K3XB7RJNEGRD8GGK42UDBCQQN4HUMB483H"
            }

        r = requests.get(self.url, params=self.params)
        json_data = json.loads(r.text)["result"]
        df = pd.json_normalize(json_data)
        df = df[["timeStamp", "hash", "nonce", "blockHash", "transactionIndex", "from", "to", "value",
         "gas", "gasPrice", "gasUsed"]]

        return df


class TokenTransferEvents:

    def __int__(self, ContractAddress: str):
        self.url = 'https://api.etherscan.io/api'
        self.params = {
            'module': 'account',
            'action': 'tokennfttx',
            'address': ContractAddress,
            'page': 1,
            'offset': 100,
            'startblock': 0,
            'endblock': 27025780,
            'sort': 'asc',
            'apikey': "K3XB7RJNEGRD8GGK42UDBCQQN4HUMB483H"
            }

        r = requests.get(self.url, params=self.params)
        json_data = json.loads(r.text)["result"]
        df = pd.json_normalize(json_data)
        #df = df[["timeStamp", "hash", "nonce", "blockHash", "transactionIndex", "from", "to", "value",
         #"gas", "gasPrice", "gasUsed"]]

        return df


#Dictionary for the ContractAdresses of the NFT Collections we are getting the Data from
Contract_Adresses = {
    "Bored Ape Yacht Club": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",
    "CryptoPunks": "0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb",
    "Mutant Ape Yacht Club": "0x60e4d786628fea6478f785a6d7e704777c86a7c6",
    "Otherdeed for Otherside": "0x34d85c9cdeb23fa97cb08333b511ac86e1c4e258",
    "Azuki": "0xed5af388653567af2f388e6224dc7c4b3241c544",
    "Clone X - X Takashi": "0x49cf6f5d44e70224e2e23fdcdd2c053f30ada28b",
    "Moonbirds": "0x23581767a106ae21c074b2276d25e5c3e136a68b",
    "Doodles": "0x8a90cab2b38dba80c64b7734e58ee1db38b8992e",
    "Bored Ape Kennel Club": "0xba30e5f9bb24caa003e9f2f0497ad287fdf95623",
    "The Sandbox": "0x5cc5b05a8a13e3fbdb0bb9fccd98d38e50f90c38"

}


#Combining all of the NFT Transaction Informations in one DataFrame:
def getDF(Contract_Adresses: dict):

    adresses = Contract_Adresses.values()
    dfs = []

    for i in adresses:
        run = TokenTransferEvents().__int__(i)
        df_A = pd.DataFrame(run)
        dfs.append(df_A)

    df = pd.concat(dfs)
    return df


df = getDF(Contract_Adresses)

#df = TokenTransferEvents().__int__("0x34d85c9cdeb23fa97cb08333b511ac86e1c4e258")
print(df.info())


def DataSelection(DataFrame, column):
    df = DataFrame.drop_duplicates(subset=[column])
    return df


pd.set_option('display.max_rows', None)

df_Drop = DataSelection(df, "transactionIndex")

print(df_Drop)

#print(TTE['from'].value_counts())
#print(TTE['to'].value_counts())

#print(TTE[TTE['tokenID'] == '2'])






#Class to read in a final Dataset to make Analysis and return results
class Analyse_Dataset:
    def __init__(self, data):
        self.data = data

    def show_data(self):
        print(self.data.head())



####### Data Visualization ####################################################################

import networkx as nx
import scipy as sp

def CentralityGraph(df):
    # Convert DataFrame into an adjacency list
    edges = []
    for index, row in df.iterrows():
        edge = (row['from'], row['to'], {'tokenID': row['tokenID'], 'gasUsed': row['gasUsed']})
        edges.append(edge)

    # Create graph object
    G = nx.Graph()
    G.add_edges_from(edges)

    # Compute centrality
    centrality = nx.betweenness_centrality(G, k=10, endpoints=True)

    # Dictionary for mapping node names to scores of 'centrality'
    node_centrality = dict(centrality)

    top_nodes = sorted(node_centrality, key=node_centrality.get, reverse=True)[:10]

    node_labels = {node: node for node in top_nodes}

    # Compute community structure
    lpc = nx.community.label_propagation_communities(G)
    community_index = {n: i for i, com in enumerate(lpc) for n in com}

    # Draw graph
    nx.draw(G, node_color=[community_index[n] for n in G], node_size=[v * 2000 for v in centrality.values()], labels=node_labels)
    plt.show()


def NetworkGraph(df):
    G = nx.from_pandas_edgelist(df, source='from', target='to')
    nx.draw_spring(G)
    plt.show()

CentralityGraph(df)






