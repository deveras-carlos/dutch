# Use the official nginx image from Docker Hub
FROM nginx:alpine

# Copy custom configuration file if needed
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]