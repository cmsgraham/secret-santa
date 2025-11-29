#!/bin/bash

# nameinahat.com Mail Server Management Script

set -e

show_help() {
    echo "📧 nameinahat.com Mail Server Management"
    echo "======================================"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start      - Start the mail server"
    echo "  stop       - Stop the mail server"
    echo "  restart    - Restart the mail server"
    echo "  logs       - Show mail server logs"
    echo "  status     - Show mail server status"
    echo "  test       - Test mail server configuration"
    echo "  adduser    - Add a new email user"
    echo "  backup     - Backup mail data"
    echo "  restore    - Restore mail data from backup"
    echo "  help       - Show this help message"
}

start_server() {
    echo "🚀 Starting nameinahat.com mail server..."
    docker-compose up -d
    echo "✅ Mail server started"
    echo "📊 Use '$0 status' to check server status"
}

stop_server() {
    echo "🛑 Stopping nameinahat.com mail server..."
    docker-compose down
    echo "✅ Mail server stopped"
}

restart_server() {
    echo "🔄 Restarting nameinahat.com mail server..."
    docker-compose restart
    echo "✅ Mail server restarted"
}

show_logs() {
    echo "📋 nameinahat.com mail server logs:"
    docker-compose logs -f nameinahat-mail
}

show_status() {
    echo "📊 nameinahat.com Mail Server Status"
    echo "=================================="
    
    if docker-compose ps | grep -q "nameinahat-mail.*Up"; then
        echo "✅ Mail server is running"
        
        # Show container stats
        echo ""
        echo "📈 Container Statistics:"
        docker stats --no-stream nameinahat-mailserver
        
        # Show port status
        echo ""
        echo "🔌 Port Status:"
        docker-compose ps
        
    else
        echo "❌ Mail server is not running"
        echo "Use '$0 start' to start the server"
    fi
}

test_server() {
    echo "🧪 Testing nameinahat.com mail server..."
    
    # Check if container is running
    if ! docker-compose ps | grep -q "nameinahat-mail.*Up"; then
        echo "❌ Mail server is not running"
        return 1
    fi
    
    # Test SMTP connectivity
    echo "📧 Testing SMTP connectivity..."
    if timeout 5 bash -c "</dev/tcp/localhost/2587"; then
        echo "✅ SMTP port 2587 is accessible"
    else
        echo "❌ SMTP port 2587 is not accessible"
    fi
    
    # Test IMAP connectivity
    echo "📬 Testing IMAP connectivity..."
    if timeout 5 bash -c "</dev/tcp/localhost/2993"; then
        echo "✅ IMAPS port 2993 is accessible"
    else
        echo "❌ IMAPS port 2993 is not accessible"
    fi
    
    # Check SSL certificates
    echo "🔒 Checking SSL certificates..."
    if [[ -f "ssl/fullchain.pem" && -f "ssl/privkey.pem" ]]; then
        echo "✅ SSL certificates are present"
        
        # Check certificate validity
        if openssl x509 -checkend 86400 -noout -in ssl/fullchain.pem; then
            echo "✅ SSL certificate is valid"
        else
            echo "⚠️  SSL certificate expires within 24 hours"
        fi
    else
        echo "❌ SSL certificates not found"
    fi
    
    echo ""
    echo "📋 Configuration Status:"
    echo "  • DKIM keys: $([ -f config/opendkim/keys/nameinahat.com/mail.private ] && echo "✅ Present" || echo "❌ Missing")"
    echo "  • Mail accounts: $([ -f config/postfix-accounts.cf ] && echo "✅ Configured" || echo "❌ Not configured")"
    echo "  • Mail data: $([ -d data/maildata ] && echo "✅ Directory exists" || echo "❌ Directory missing")"
}

add_user() {
    echo "➕ Add New Email User to nameinahat.com"
    echo "===================================="
    
    read -p "Enter email address: " email
    read -s -p "Enter password: " password
    echo ""
    
    # Validate email format
    if [[ ! "$email" =~ @nameinahat\.com$ ]]; then
        echo "❌ Email must be @nameinahat.com"
        return 1
    fi
    
    # Generate password hash
    password_hash=$(python3 -c "import crypt; print(crypt.crypt('$password', crypt.mksalt(crypt.METHOD_SHA512)))")
    
    # Add to postfix-accounts.cf
    echo "$email|$password_hash" >> config/postfix-accounts.cf
    
    # Add quota (default 500MB)
    echo "$email:524288000" >> config/dovecot-quotas.cf
    
    echo "✅ User $email added successfully"
    echo "🔄 Restart the mail server to apply changes: $0 restart"
}

backup_data() {
    echo "💾 Backing up mail server data..."
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="mailserver_backup_${timestamp}.tar.gz"
    
    tar -czf "$backup_file" data/ config/ ssl/ .mail-credentials docker-compose.yml
    
    echo "✅ Backup created: $backup_file"
    echo "📁 Backup includes: data, config, SSL certificates, and credentials"
}

restore_data() {
    echo "📥 Restore mail server data from backup"
    echo "====================================="
    
    # List available backups
    backups=(mailserver_backup_*.tar.gz)
    
    if [ ${#backups[@]} -eq 0 ] || [ ! -f "${backups[0]}" ]; then
        echo "❌ No backup files found"
        return 1
    fi
    
    echo "Available backups:"
    for i in "${!backups[@]}"; do
        echo "  $((i+1)). ${backups[i]}"
    done
    
    read -p "Select backup to restore (1-${#backups[@]}): " choice
    
    if [[ "$choice" -gt 0 && "$choice" -le "${#backups[@]}" ]]; then
        selected_backup="${backups[$((choice-1))]}"
        
        echo "⚠️  This will overwrite current configuration and data!"
        read -p "Continue? (y/N): " confirm
        
        if [[ "$confirm" == [yY] ]]; then
            # Stop server first
            stop_server
            
            # Extract backup
            tar -xzf "$selected_backup"
            
            echo "✅ Data restored from $selected_backup"
            echo "🚀 Starting mail server with restored data..."
            start_server
        else
            echo "❌ Restore cancelled"
        fi
    else
        echo "❌ Invalid selection"
    fi
}

# Main command handling
case "${1:-help}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    test)
        test_server
        ;;
    adduser)
        add_user
        ;;
    backup)
        backup_data
        ;;
    restore)
        restore_data
        ;;
    help|*)
        show_help
        ;;
esac