# Flipkart Price Tracker with RSS
There are some nice open source trackers available for Price Tracking Flipkart products, none of them generated an 
RSS Feed.

## Output
Atom-formatted web feed with product's price, image URL and title.

## Inspiration
https://github.com/captn3m0/ideas#-amazon-price-tracker-with-rss

The feed url will be of the form, `http://localhost:12564/flipkart?link=<Product page url>`

_Add extra param for adding constant data to feed_. Example:
`http://localhost:12564/flipkart?link=<Product page url>?my_price=1000`
This wont do anything other than returning it with the feed. It can be used as a note! :p