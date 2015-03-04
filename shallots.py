#class shallots(object):

def add_languages_mongo():
    pass

def make_sql_database():
    pass

def fill_mongoref_sql_database():
    pass

def fill_sitesite_relations():
    pass

def fill_countries():
    pass

def clean_tokenize_text():
    #remove ascii
    #lower
    #stem
    pass

def find_clusters():
    pass

def get_cluster_description():
    pass

def store_clus_desc():
    pass

def similar_extract():
    pass

if __name__ == '__main__':
    #shal = shallots()
    #add "language" field to mongodb
    add_languages_mongo()
    #make database & tables postgres
    make_sql_database()
    #fill tables with referrals to mongo ID (filter on english language)
    fill_mongoref_sql_database()
    #extract urls (domains) and store in table
    fill_sitesite_relations()
    #extract countries and store in table
    fill_countries()
    #tokenize and cluster
    clean_tokenize_text()
    find_clusters()
    #get description
    get_cluster_description()
    #store clusters and their description
    store_clus_desc
    '''handwork annotating legal/illegal'''
    #within clusters, do similar concept extraction and store in table
    similar_extract()
    #visualize (tell flask to prepare everything)
