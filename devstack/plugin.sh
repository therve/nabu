# check for service enabled
if is_service_enabled nabu-api; then
    if [[ "$1" == "source" ]]; then
        # Initial source of lib script
        source $(dirname "$0")/lib/nabu
    fi

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        # Set up system services
        echo_summary "Configuring system services nabu"
        pre_install_nabu

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        # Perform installation of service source
        echo_summary "Installing nabu"
        install_nabu

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configuring nabu"
        configure_nabu

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # Initialize and start the nabu service
        echo_summary "Initializing nabu"
        init_nabu
    fi

    if [[ "$1" == "unstack" ]]; then
        # Shut down nabu services
        # no-op
        shutdown_nabu
    fi

    if [[ "$1" == "clean" ]]; then
        # Remove state and transient data
        # Remember clean.sh first calls unstack.sh
        # no-op
        cleanup_nabu
    fi
fi
