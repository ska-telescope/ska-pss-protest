# PSS-SDP Interface Feature Files

This directory contains Gherkin feature files that define the behavior-driven development (BDD) specifications for the PSS (Pulsar Search Sub-system) to SDP (Science Data Processor) interface.

## Feature Files Overview

### [candidate_streaming.feature](candidate_streaming.feature)

Defines scenarios for streaming candidate data from PSS to SDP using network protocols.

| Scenario | Description |
|----------|-------------|
| Stream single pulse candidate data to SDP | Verifies transmission of detected candidates to configured endpoints |
| Transmitted data contains required candidate fields | Validates presence of DM, S/N, pulse time, pulse width, and sigma |
| Transmitted data contains time-frequency data descriptors | Ensures time-frequency metadata is included in payloads |
| Configure network endpoint for candidate streaming | Tests endpoint configuration with various IP/port combinations |
| Stream candidates to multiple network endpoints | Verifies multi-endpoint transmission capability |
| Transmitted candidate field maintains integrity | Confirms each field value is preserved during transmission (5 fields tested) |
| Network streaming handles high candidate rates | Tests performance under high candidate detection rates with <delay> max delay |

### [error_handling_resilience.feature](error_handling_resilience.feature)

Defines scenarios for error handling, fault tolerance, and system resilience.

| Scenario | Description |
|----------|-------------|
| Handle packets with invalid headers | Graceful handling of malformed packet headers |
| Handle network endpoint unreachable | Behaviour when network endpoint becomes unavailable |
| Handle packet loss during transmission | Recovery from network congestion and packet loss |
| Recover from receiver pod restart | Kubernetes pod restart recovery |
| Handle persistent volume storage exhaustion | Storage capacity exhaustion handling |
| Handle invalid exporter configuration | Configuration validation and error reporting |
| Handle malformed data payload | Deserialisation error handling |
| Handle receiver job deadline exceeded | Kubernetes job deadline management |
| Retry connection to network endpoint on failure | Connection retry with exponential backoff |
| Clean up resources on pipeline shutdown | Graceful shutdown and resource cleanup |
| Handle duplicate candidate data reception | Duplicate detection and filtering |
| Handle transmission timeout | Timeout handling and recovery |
| Validate candidate data before transmission | Pre-transmission data validation |

### [pss_sdp_integration.feature](pss_sdp_integration.feature)

Defines end-to-end integration scenarios verifying the complete PSS to SDP data flow.

| Scenario | Description |
|----------|-------------|
| Complete single pulse candidate transmission from PSS to SDP | Full pipeline verification from detection to storage |
| Interface handles expected data rates | Data rate and throughput verification |
| Handle candidate data from multiple beams | Multi-beam candidate processing |
| Verify protocol compatibility between PSS and SDP | Protocol version and compatibility checks |
| Verify Kubernetes deployment of interface components | Deployment and service verification |
| Process candidate data throughout an observation session | Full observation session testing |
| Apply calibration data during candidate processing | Calibration integration verification |
| Meet latency requirements for real-time candidate transmission | Latency budget compliance |
| Monitor interface health and performance | Monitoring and alerting verification |

### [sdp_candidate_reception.feature](sdp_candidate_reception.feature)

Defines scenarios for SDP receiving and processing candidate data from PSS.

| Scenario | Description |
|----------|-------------|
| Receive single pulse candidate data from PSS | Basic data reception on configured port (1 test case) |
| Store received candidate metadata to persistent volume | Persistent storage of candidate data |
| Receive SPCCL formatted candidate data | SPCCL format handling and storage |
| SDP receiver is accessible via Kubernetes service | Kubernetes service routing verification |
| Receiver initialises Cheetah data exporter successfully | Initialisation and readiness checks |
| Receiver job runs until completion or timeout | Job lifecycle management |
| Extract individual candidate fields from received data | Payload deserialisation and field extraction |
| Verify persistent volume has sufficient capacity | Storage capacity verification |
| Handle multiple concurrent data streams | Multi-beam concurrent reception |

### [pss_sdp_configuration.feature](pss_sdp_configuration.feature)

Defines scenarios for configuring the PSS-SDP interface parameters and components.

| Scenario | Description |
|----------|-------------|
| Configure PSS exporter via XML configuration file | XML-based pipeline configuration loading |
| Configure different exporter sink types | Sink type configuration for sigproc, SPCCL, network, and SCL outputs |
| Map channels to configured sinks | Channel-to-sink routing configuration |
| Configure SDP receive addresses using ska-sdp-recvaddrs schema | Schema-based SDP endpoint configuration |
| Configure host mapping for channel-based addressing | Channel-to-host address mapping |
| Configure port mapping with increment calculation | Port allocation using start/increment pattern (3 test cases) |
| Configure file streamer output parameters | File exporter directory and extension settings (1 test case) |
| Configure network streaming endpoint | Network exporter IP and port configuration |
| Configure sink processing threads | Thread pool configuration for parallel export (1 test case) |
| Verify beam configuration is available | Check configured beams are detected (2 test cases) |
| Configure pss-receive listening parameters | UDP listener interface and port configuration |
| Configure pss-receive output storage location | Persistent volume output directory configuration (1 test case) |
| Configure pss-receive output file naming pattern | File naming pattern to avoid collisions |
| PSS and SDP configurations align for data flow | End-to-end configuration coordination verification |
| Configure multiple independent beams with unique endpoints | Multi-beam port assignment and isolation (1 test case) |
| Apply default configuration values for optional parameters | Configuration defaults and fallback behavior |

---

## Key Principles Applied

1. **One Scenario, One Behavior**: Each scenario covers a single, independent behavior
2. **Declarative Steps**: Steps describe what happens, not how (hiding implementation details)
3. **Third-Person Point of View**: All steps use third-person for consistency
4. **Present Tense**: Steps use present tense throughout
5. **Clear Titles**: Scenario titles concisely describe the behavior being tested
6. **Parameterised Examples**: Scenario Outlines with Examples tables for variations
7. **Tags for Organisation**: Tags indicate XTP ticket references and test categories

---

## Tag Conventions

| Tag | Description |
|-----|-------------|
| `@pss-sdp-interface` | All PSS-SDP interface scenarios |
| `@XTP-TBD` | Placeholder for JIRA XTP ticket reference (to be assigned) |
| `@happy-path` | Normal/expected operation scenarios |
| `@error-handling` | Error and exception scenarios |
| `@configuration` | Configuration-related scenarios |
| `@integration` | End-to-end integration scenarios |
| `@smoke` | Quick verification tests |

### Additional Tags Used

| Tag | Description |
|-----|-------------|
| `@streaming` | Network streaming related scenarios |
| `@network` | Network communication scenarios |
| `@resilience` | System resilience and recovery scenarios |
| `@end-to-end` | Full end-to-end flow scenarios |
| `@sdp-receive` | SDP receiver component scenarios |
| `@data-ingestion` | Data ingestion and processing scenarios |
| `@data-storage` | Persistent storage scenarios |
| `@data-integrity` | Data integrity verification scenarios |
| `@data-rate` | Data rate and throughput scenarios |
| `@data-validation` | Data validation scenarios |
| `@performance` | Performance related scenarios |
| `@kubernetes-service` | Kubernetes service related scenarios |
| `@multi-beam` | Multi-beam processing scenarios |
| `@multiple-endpoints` | Multi-endpoint configuration scenarios |
| `@protocol-compatibility` | Protocol compatibility scenarios |
| `@deployment-verification` | Deployment verification scenarios |
| `@observation-session` | Observation session scenarios |
| `@calibration-integration` | Calibration integration scenarios |
| `@latency-requirements` | Latency requirement scenarios |
| `@monitoring-integration` | Monitoring and observability scenarios |
| `@invalid-header` | Invalid packet header scenarios |
| `@network-unreachable` | Network unreachable scenarios |
| `@packet-loss` | Packet loss handling scenarios |
| `@receiver-restart` | Receiver restart recovery scenarios |
| `@storage-exhaustion` | Storage exhaustion scenarios |
| `@configuration-error` | Configuration error scenarios |
| `@deserialisation-error` | Deserialisation error scenarios |
| `@job-deadline-exceeded` | Job deadline scenarios |
| `@connection-retry` | Connection retry scenarios |
| `@resource-cleanup` | Resource cleanup scenarios |
| `@duplicate-detection` | Duplicate data detection scenarios |
| `@timeout-handling` | Timeout handling scenarios |
| `@ska-sdp-recvaddrs` | SKA SDP receive address schema scenarios |
| `@xml-configuration` | XML configuration file scenarios |
| `@sink-configuration` | Exporter sink configuration scenarios |
| `@channel-sink-mapping` | Channel-to-sink routing scenarios |
| `@recvaddrs-schema` | Receive address schema scenarios |
| `@host-mapping` | Host address mapping scenarios |
| `@port-mapping` | Port mapping and allocation scenarios |
| `@file-exporter-config` | File exporter configuration scenarios |
| `@network-endpoint-config` | Network endpoint configuration scenarios |
| `@threads-configuration` | Thread configuration scenarios |
| `@beam-activation` | Beam activation/deactivation scenarios |
| `@pss-receive-config` | PSS-receive component configuration scenarios |
| `@pss-receive-storage` | PSS-receive storage configuration scenarios |
| `@pss-receive-file-naming` | PSS-receive file naming scenarios |
| `@config-coordination` | Configuration coordination scenarios |
| `@multi-beam-config` | Multi-beam configuration scenarios |
| `@default-values` | Configuration default value scenarios |

---

## Running Feature Tests

TODO add this section when detailing test automation

