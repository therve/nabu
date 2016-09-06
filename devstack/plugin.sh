# Install and start nabu in devstack

function install_nabu {
    # Install the service.
    setup_develop $NABU_DIR
}

function configure_nabu {
    # Configure the service.
    cp $NABU_DIR/etc/nabu/api-paste.ini $NABU_API_PASTE_FILE

    if is_service_enabled ceilometer-collector; then
        iniset $CEILOMETER_CONF DEFAULT event_dispatchers nabu
    fi
}

function init_nabu {
    create_nabu_accounts
    # Initialize and start the service.
    recreate_database nabu

    $NABU_BIN_DIR/nabu-manage upgrade
}

function start_nabu {
    run_process nabu-api "$NABU_BIN_DIR/nabu-wsgi-api --config-file=$NABU_CONF"
}

function stop_nabu {
    # Shut the service down.
    stop_process nabu-api
}

function create_nabu_accounts {
    create_service_user "nabu"

    local nabu_service=$(get_or_create_service "nabu" \
        "subscription" "Nabu Service")
    get_or_create_endpoint $nabu_service \
        "$REGION_NAME" \
        "$NABU_SERVICE_PROTOCOL://$NABU_SERVICE_HOST:$NABU_SERVICE_PORT" \
        "$NABU_SERVICE_PROTOCOL://$NABU_SERVICE_HOST:$NABU_SERVICE_PORT" \
        "$NABU_SERVICE_PROTOCOL://$NABU_SERVICE_HOST:$NABU_SERVICE_PORT"

}


# check for service enabled
if is_service_enabled nabu-api; then
    if [[ "$1" == "source" ]]; then
        # Initial source of lib script
        source $(dirname "$0")/lib/nabu
    fi

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        # Set up system services
        echo_summary "Configuring system services nabu"

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
        start_nabu
    fi

    if [[ "$1" == "unstack" ]]; then
        # Shut down nabu services
        stop_nabu
    fi

    if [[ "$1" == "clean" ]]; then
        # Remove state and transient data
        # Remember clean.sh first calls unstack.sh
	echo_summary "Cleanup nabu"
    fi
fi
