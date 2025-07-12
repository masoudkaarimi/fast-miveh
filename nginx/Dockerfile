FROM nginx:latest

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/

# Create necessary directories
RUN mkdir -p /usr/src/staticfiles /usr/src/media /usr/src/logs

EXPOSE 80 443

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]