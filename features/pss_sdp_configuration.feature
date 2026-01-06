@pss-sdp-interface @configuration @ska-sdp-recvaddrs
Feature: PSS-SDP Interface Configuration
  As a system integrator
  I want to configure the PSS-SDP interface parameters
  So that candidate data flows correctly between systems

  Background:
    Given the PSS pipeline configuration file is available
    And the SDP receive address schema is defined

  # TODO: Confirm configuration format with Ben Shaw (XML or JSON)
  @XTP-TBD @pipeline-configuration
  Scenario: Configure PSS exporter via configuration file
    Given a configuration file with beam settings exists
    When the configuration specifies sinks for the beam
    Then the DataExport module loads the sink configurations
    And the exporters are initialised according to the configuration

  @XTP-TBD @sink-configuration
  Scenario Outline: Configure different exporter sink types
    Given the sink_configs section of the configuration
    When a sink of type "<sink_type>" is configured with id "<sink_id>"
    Then the exporter factory creates an instance of the correct type
    And the exporter is associated with the specified id

    Examples:
      | sink_type           | sink_id              |
      | sigproc             | sigproc_output       |
      | spccl_files         | spccl_file_output    |
      | network             | network_output       |
      | scl_candidate_data  | scl_output           |

  @XTP-TBD @stream-sink-mapping
  Scenario: Map output streams to configured sinks
    Given the outputs section defines a single pulse events stream
    And the stream references a configured SPCCL file sink
    When the pipeline processes single pulse events
    Then the events are routed to the SPCCL file exporter

  @XTP-TBD @recvaddrs-schema @combined-search
  Scenario: Configure SDP receive addresses for combined transient and FDAS search
    Given the ska-sdp-recvaddrs schema is used
    When the PSS beam configuration is defined for combined search mode
    Then the search_beam_id identifies the pulsar search beam
    And the function is set to combined transient and FDAS search mode
    And both single pulse and FDAS candidate outputs are configured

  @XTP-TBD @recvaddrs-schema @transient-search
  Scenario: Configure SDP receive addresses for transient search only
    Given the ska-sdp-recvaddrs schema is used
    When the PSS beam configuration is defined for transient search mode
    Then the search_beam_id identifies the pulsar search beam
    And the function is set to transient search mode
    And only single pulse candidate outputs are configured

  @XTP-TBD @recvaddrs-schema @fdas-search
  Scenario: Configure SDP receive addresses for FDAS search only
    Given the ska-sdp-recvaddrs schema is used
    When the PSS beam configuration is defined for FDAS search mode
    Then the search_beam_id identifies the pulsar search beam
    And the function is set to FDAS search mode
    And only FDAS candidate outputs are configured

  @XTP-TBD @host-mapping
  Scenario: Configure host mapping for node-based addressing
    Given the ska-sdp-recvaddrs configuration for PSS
    When host mapping is defined with processing node and host address
    Then multiple processing nodes can map to different hosts
    And the receiver resolves host addresses correctly

  @XTP-TBD @port-mapping
  Scenario Outline: Configure port mapping with increment calculation
    Given the port mapping defines start_channel "<start>", start_port "<port>", and increment "<inc>"
    When calculating the port for channel "<channel>"
    Then the resulting port is "<result>"

    Examples:
      | start | port | inc | channel | result |
      | 0     | 9021 | 1   | 0       | 9021   |
      | 0     | 9021 | 1   | 5       | 9026   |
      | 10    | 9030 | 2   | 15      | 9040   |


  @XTP-TBD @file-exporter-config
  Scenario Outline: Configure file streamer output parameters
    Given a file-based exporter configuration
    When the output directory is set to "<output_directory>"
    And the file extension is set to ".spccl"
    Then the exporter writes files to the specified directory
    And files are created with the specified extension

    Examples:
      | output_directory    |
      | /output/candidates  |

  @XTP-TBD @network-endpoint-config
  Scenario: Configure network streaming endpoint
    Given a network exporter configuration
    When the endpoint is configured with the following settings
      | parameter  | value           |
      | port       | 9021            |
      | ip_address | 192.168.1.100   |
    Then the network streamer connects to the specified endpoint

  @XTP-TBD @threads-configuration
  Scenario Outline: Configure sink processing threads
    Given the sinks configuration section
    When the threads parameter is set to <thread_count>
    Then the sink processing uses the configured number of threads
    And data export is parallelised appropriately

    Examples:
      | thread_count |
      | 2            |

  @XTP-TBD @beam-configuration
  Scenario Outline: Verify beam configuration is available
    Given the pipeline configuration file is loaded
    When checking for configured beams
    Then <beam_count> beam(s) are detected in the configuration
    And each beam has valid export sink settings

    Examples:
      | beam_count |
      | 1          |
      | 4          |

  @XTP-TBD @pss-receive-config
  Scenario: Configure pss-receive listening parameters
    Given the pss-receive deployment configuration
    When the UDP listening port is set to 9021
    And the listening interface is set to "0.0.0.0"
    Then the receiver listens on all interfaces on the specified port
    And incoming candidate data packets are accepted

  @XTP-TBD @pss-receive-storage
  Scenario Outline: Configure pss-receive output storage location
    Given the pss-receive container configuration
    When the output directory is set to "<output_directory>"
    Then received candidate data is written to the configured directory
    And the persistent volume mount point is respected

    Examples:
      | output_directory    |
      | /output/candidates  |

  @XTP-TBD @pss-receive-file-naming
  Scenario: Configure pss-receive output file naming pattern
    Given the pss-receive file output configuration
    When the filename pattern includes beam identifier and timestamp
    Then output files are created with unique identifiable names
    And file collisions are avoided across multiple beams

  @XTP-TBD @config-coordination
  Scenario: PSS and SDP configurations align for data flow
    Given the PSS network exporter is configured with endpoint "pss-receive:9021"
    And the SDP pss-receive service is listening on port 9021
    When the configurations are validated
    Then the PSS endpoint resolves to the SDP service
    And data can flow from PSS to SDP

  @XTP-TBD @multi-beam-config
  Scenario Outline: Configure multiple independent beams with unique endpoints
    Given the configuration defines <beam_count> pulsar search beams
    When each beam is assigned a unique port in range <start_port>-<end_port>
    Then each beam exports candidate data to its designated endpoint
    And beam data streams remain independent

    Examples:
      | beam_count | start_port | end_port |
      | 4          | 9021       | 9024     |

  @XTP-TBD @default-values
  Scenario: Apply default configuration values for optional parameters
    Given a minimal PSS exporter configuration
    When optional parameters are omitted
    Then default thread count is applied
    And default timeout values are used
    And the pipeline initialises successfully with defaults
