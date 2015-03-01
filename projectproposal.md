<h2>Capstone project proposal</h2>

<b>Working Title: "Shallots: Shining the light on the deep web, analysis of what is beneath the surface of the internet"</b>

<i>Summary</i>

The deep web has a lot of secrets. My goal is to give some insight in what is going on there. I'll describe the main topics that are discussed there and give insight in their meaning. I'll divide the clusters into 2 groups (legal/illegal) and find out if they behave like 2 separate islands or are actually connected. And last I'll geographically plot the countries talked about in relation to the clusters. It will start with crawled deep web html content and it will end with a website with visualizations.  

<i>Description</i>

Tor is software for enabling anonymous online communication. It is meant to provide safety for vulnerable internet users such as political activists. The downside, however, is that it facilitates criminals that use servers that can only receive connections through Tor, to make it hard to get identified. Those servers are called hidden services and can be accessed through an .onion address. 

Not much research has been done on what is going on in this "deep web". There was some content clustering, which showed that both legal and illegal content is available on websites. It is not clear how connected those 2 groups are. 

<i>Motivation</i>

In 2011 I first encountered the illegal side of the deep web. Since then it kept surprising me that tools and analysts that focus on the internet, normally don't take the deep web into account. They actually should in my opinion because this is especially the place where things can come to the surface since users feel save by the anonymizing function of Tor. 

It is an ideal way to combine my interest in the deep web with my preference for NLP and social network analysis (SNA) into one project. And it can grow along the way, if there is time, looking further into insights I get during the analysis.

<i>Personal and learning objectives</i><br>
I'd like to use this project to learn more about controlling data flows while scraping (if needed), NLP and visualization.

<i>Deliverables</i><br>
The project results will be shown on a website. 

<i>Data Sources</i><br>
Crawled deep web data stored in mongoDB, crawled by the builder of Ahmia and OnionBot.
<a href=https://github.com/juhanurmi/ahmia/tree/master/onionbot>OnionBot</a>

<i>Project Details</i>

<i>Process</i>
<br><s>-Get the scraped html content stored in MongoDB</s>
<br>-Check the scraped data
<br>-Find .onion links in result (regex?) and fill the relations table with that (id, id) in SQL
<br>-Clear html from content
<br>-Bag of words, clustering, with k=10
<br>-Read cluster top x words to decide what the best descriptive word is, if not clear, change k
<br>-Store manually decided name, legal/illegal in table with cluster
<br>-NER on country names for visualization
<br>-Create concept graph data of similar words with word2vec
<br>-Create website somewhere (decide where)
<br>-Visualize 
<ul>
<li>Barchart with on click -> concept graph of specific cluster, wordcloud?</li>
<li>Gephi grouped clusters with relations between them based on url references</li>
<li>Map of the world with spectrum red-green based on legal/illegal with on click -> piechart of clusters</li>
<li>.... </li>
</ul>
-If time left Explore other possible interesting features -> weighting based on html tag

<i>Architecture & implementation</i>
<br>-Python
<br>-MongoDB
<br>-PostgreSQL
<br>-Gephi
<br>-matplotlib/d3.js/plot.ly?
<br>-GIS?
<br>-NER from stanford
<br>-Gensim
<br>-Clustering (kmeans?)

<i>Data features</i>
<br>Mongo crawl result : site_id, url, content, title, timestamp, (language)
<br>Feature matrix: site_id, cluster, countries
<br>Clusters: cluster, name, legal/illegal, describing_words 
<br>Clusterwordvec: cluster, word, word, simscore
<br>Relations: site_id, site_id (relations)

<i>Challenges</i>
<br>Known so far:
<br><s>-Get most random results by giving right priority to crawler</s>
<br><s>-Fast enough to get enough data in time</s>
<br><s>-Getting it to work on amazon & storage</s>

<i>Timeline</i>
<br>tbd, deadline March 19th

<i>References</i>
<br>https://blog.torproject.org/category/tags/crawling 
<br>http://arxiv.org/pdf/1308.6768v2.pdf
<br>http://www.dis.uniroma1.it/~dasec/DASec_Pustogarov.pdf
<br>https://www.gwern.net/docs/sr/2014-spitters.pdf
<br>https://github.com/juhanurmi/ahmia/tree/master/onionbot

<i>Todo</i>
<br><s>Contact juhanurmi</s>
<br><s>Find catchy name</s>
<br><s>Decide how many words/depth needed per domain/site (don't need to crawl the whole forum)</s>
<br><s>Language detection/filtering</s>
<br><s>Maximize random crawling algo</s>
<br>datasets: 
<br><s>-startlist</s>
<br><s>-content</s>
<br>-featurematrix
<br>-relations table
