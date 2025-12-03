#!/bin/bash

# Email Blacklist/Whitelist Management Script Wrapper
# Provides easy interface to check and manage email blacklist/whitelist

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/email_blacklist_management.py"

show_help() {
    cat << 'EOF'
📧 Email Blacklist/Whitelist Management Tool
=============================================

Usage: ./email_management.sh [command] [options]

Commands:
  check <email>              Check email deliverability and blacklist status
  whitelist <email> [notes]  Whitelist an email address
  blacklist <email> [reason] Blacklist an email address
  list                       List all blacklisted emails
  whitelist-list             List all whitelisted emails
  report                     Generate email status report
  help                       Show this help message

Examples:
  ./email_management.sh check cristian.madrigal@gmail.com
  ./email_management.sh whitelist user@example.com "Valid customer"
  ./email_management.sh blacklist spam@example.com "Unverified address"
  ./email_management.sh report
  ./email_management.sh list

EOF
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is required but not installed${NC}"
        exit 1
    fi
}

check_dependencies() {
    # Try importing in Python directly
    python3 -c "import dns.resolver; import email_validator" 2>/dev/null && return 0
    
    # If import fails, suggest installation
    echo -e "${YELLOW}⚠️  Some optional features require Python packages${NC}"
    echo "    Run: pip3 install --user dnspython email-validator python-dotenv"
    echo "    Or use a virtual environment"
    echo ""
}

run_command() {
    check_python
    check_dependencies
    python3 "$PYTHON_SCRIPT" "$@"
}

main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    case "$1" in
        help|-h|--help)
            show_help
            ;;
        check)
            if [ -z "$2" ]; then
                echo -e "${RED}❌ Email address required${NC}"
                echo "Usage: $0 check <email>"
                exit 1
            fi
            echo -e "${BLUE}🔍 Checking email: $2${NC}"
            run_command check "$2"
            ;;
        whitelist)
            if [ -z "$2" ]; then
                echo -e "${RED}❌ Email address required${NC}"
                echo "Usage: $0 whitelist <email> [notes]"
                exit 1
            fi
            notes="${3:-Whitelisted}"
            echo -e "${BLUE}✨ Whitelisting email: $2${NC}"
            run_command whitelist "$2" --notes "$notes"
            ;;
        blacklist)
            if [ -z "$2" ]; then
                echo -e "${RED}❌ Email address required${NC}"
                echo "Usage: $0 blacklist <email> [reason]"
                exit 1
            fi
            reason="${3:-Manual addition}"
            echo -e "${BLUE}🚫 Blacklisting email: $2${NC}"
            run_command blacklist "$2" --reason "$reason"
            ;;
        list)
            echo -e "${BLUE}📋 Listing blacklisted emails${NC}"
            run_command list
            ;;
        whitelist-list)
            echo -e "${BLUE}✅ Listing whitelisted emails${NC}"
            run_command whitelist-list
            ;;
        report)
            echo -e "${BLUE}📊 Generating report${NC}"
            run_command report
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
