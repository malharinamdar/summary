# -*- coding: utf-8 -*-
import streamlit as st
from eventregistry import EventRegistry, QueryArticlesIter, QueryItems
from transformers import pipeline

# Initialize Event Registry with your API key
er = EventRegistry(apiKey='')

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Main Streamlit app code
def main():
    st.title('Article Summarizer')

    st.markdown('*Enter Keywords (comma-separated):*')
    st.markdown('Example: COVID-19, pandemic')
    keywords = st.text_input('Keywords', key='keywords_input')

    # User input for category
    st.markdown('*Enter Category:*')
    st.markdown('Example: Health, Politics, Technology')
    category = st.text_input('Category', key='category_input')

    # User input for date range
    st.markdown('*Enter Start Date (YYYY-MM-DD):*')
    dateStart = st.date_input('Start Date', key='start_date_input')
    st.markdown('*Enter End Date (YYYY-MM-DD):*')
    dateEnd = st.date_input('End Date', key='end_date_input')

    # Execute query when user clicks the button
    if st.button('Fetch Articles'):
        with st.spinner('Fetching articles...'):
            # Create a query item for keywords
            keywords_query_item = QueryItems.OR(keywords.split(','))

            # Initialize QueryArticlesIter with the constructed query
            q = QueryArticlesIter(
                keywords=keywords_query_item,
                keywordsLoc="title",
                categoryUri=er.getCategoryUri(category),
                dateStart=dateStart.strftime('%Y-%m-%d'),
                dateEnd=dateEnd.strftime('%Y-%m-%d')
            )

            # Initialize a set to store the titles of fetched articles
            fetched_titles = set()

            # Fetch and display articles
            articles = []
            for article in q.execQuery(er, sortBy="date", sortByAsc=False, maxItems=10):
                # Check if the article title is not already in the fetched titles set
                if article['title'] not in fetched_titles:
                    # Summarize the article using the summarization pipeline
                    summary_output = summarizer(' '.join(article['body'].split()[:650]), max_length=150, min_length=30, do_sample=False)

                    # Check if the summarizer output is valid
                    if summary_output and isinstance(summary_output, list) and len(summary_output) > 0:
                        # Get the first summary text from the output list
                        summary_text = summary_output[0].get('summary_text', '')

                        # Add the article to the list if the summary text is not empty
                        if summary_text:
                            articles.append({
                                "Title": article['title'],
                                "Summary": summary_text,
                                "Date": article['date'],
                                "Similarity": article['sim']
                            })
                    fetched_titles.add(article['title'])  # Add the title to the fetched titles set

        # Display the fetched articles with summaries
        st.subheader('Recent Article Summaries:')
        for article in articles:
            st.write("Title:", article['Title'])
            st.write("Summary:", article['Summary'])
            st.write("Date:", article['Date'])
            # st.write("Similarity:", article['Similarity'])
            st.write("---")

if __name__ == '__main__':
    main()
