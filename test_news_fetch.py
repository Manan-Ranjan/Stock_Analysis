import feedparser
import requests

def test_google_news(stock_symbol):
    """Test Google News RSS feed"""
    print(f"\n🔍 Testing news fetch for {stock_symbol}...")
    
    # Test queries
    queries = [
        f"{stock_symbol} stock",
        f"{stock_symbol} NSE India",
        "HDFC Bank stock news"
    ]
    
    for query in queries:
        print(f"\n📰 Query: {query}")
        url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en"
        print(f"URL: {url}")
        
        try:
            # Try with requests first
            response = requests.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            # Parse with feedparser
            feed = feedparser.parse(url)
            print(f"Feed entries found: {len(feed.entries)}")
            
            if feed.entries:
                print("\n✅ Sample articles:")
                for i, entry in enumerate(feed.entries[:3]):
                    print(f"\n{i+1}. {entry.get('title', 'No title')}")
                    print(f"   Link: {entry.get('link', 'No link')}")
                    print(f"   Published: {entry.get('published', 'No date')}")
                break
            else:
                print("❌ No entries found")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_google_news("HDFCBANK")

# Made with Bob
