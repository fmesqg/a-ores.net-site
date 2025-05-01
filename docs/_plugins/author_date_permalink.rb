module Jekyll
    class AuthorDatePermalinkGenerator < Generator
      safe true
      priority :high
  
      def generate(site)
        # First pass: collect authors
        authors = {}
        site.collections['authors'].docs.each do |author|
          authors[author.data['short_name']] = author.url
        end
  
        # Second pass: set post permalinks
        site.posts.docs.each do |post|
          # Skip posts that have custom permalinks set
          next if post.data['permalink']
          
          date = post.date
          formatted_date = date.strftime('%Y-%m-%d')
          
          # Get author from post front matter
          author_name = post.data['author']
          
          # If multiple authors, use the first one
          if author_name.is_a?(Array)
            author_name = author_name.first
          end
          
          # Get author URL, default to /authors/author_name/ if not found
          author_url = authors[author_name]
          if author_url.nil?
            author_url = "/blog/#{author_name}/"
          end
          
          # Remove trailing slash from author URL if present
          author_url = author_url.chomp('/')
          
          # Format: /authors/author_name/YYYY-MM-DD/
          custom_permalink = "#{author_url}/#{formatted_date}"
          
          # Set the permalink
          post.data['permalink'] = custom_permalink
        end
      end
    end
  end