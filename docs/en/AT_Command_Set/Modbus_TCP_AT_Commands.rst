.. _MODBUSTCP-AT:

Modbus TCP AT Commands
======================

:link_to_translation:`zh_CN:[中文]`

-  :ref:`Introduction <cmd-modbustcp-intro>`
-  :ref:`AT+MODBUSTCP <cmd-MODBUSTCP>`: Enable/disable Modbus TCP to UART bridge.

.. _cmd-modbustcp-intro:

Introduction
------------

.. important::
  This feature provides a transparent TCP-UART bridge for Modbus TCP communication. 
  The ESP32 acts as a Modbus TCP server, forwarding all received TCP data to the AT UART port, 
  and sending UART responses back to the TCP client. The actual Modbus protocol parsing 
  is handled by the external MCU connected to the UART port.

  To enable this feature, configure ``Component config`` > ``AT`` > ``AT Modbus TCP Bridge command support`` in menuconfig.

.. _cmd-MODBUSTCP:

:ref:`AT+MODBUSTCP <MODBUSTCP-AT>`: Enable/Disable Modbus TCP to UART Bridge
-----------------------------------------------------------------------------

Query Command
^^^^^^^^^^^^^

**Function:**

Query the current Modbus TCP bridge status.

**Command:**

::

    AT+MODBUSTCP?

**Response:**

::

    +MODBUSTCP:<enable>,<port>,<timeout>,<state>

    OK

Set Command
^^^^^^^^^^^

**Function:**

Enable or disable the Modbus TCP to UART bridge.

**Command:**

::

    AT+MODBUSTCP=<enable>[,<port>,<timeout>]

**Response:**

::

    OK

If the bridge starts successfully, the following URC will be reported:

::

    +MODBUSTCP:LISTENING

When a client connects:

::

    +MODBUSTCP:CONNECTED

When a client disconnects:

::

    +MODBUSTCP:DISCONNECTED

When the bridge is stopped:

::

    +MODBUSTCP:STOPPED

Parameters
^^^^^^^^^^

-  **<enable>**: Enable or disable the Modbus TCP bridge.

   -  0: Disable the bridge and stop the TCP server.
   -  1: Enable the bridge and start the TCP server.

-  **<port>**: TCP server port number. Default: 502 (standard Modbus TCP port). Range: [1,65535].
-  **<timeout>**: Connection timeout in seconds. Default: 60. Range: [1,3600].
-  **<state>**: Current bridge state (query only).

   -  ``STOPPED``: Bridge is not running.
   -  ``LISTENING``: TCP server is listening for connections.
   -  ``CONNECTED``: A TCP client is connected.

Notes
^^^^^

-  Only one TCP client can connect at a time.
-  All TCP data is transparently forwarded to the AT UART port without any modification.
-  All UART data is transparently forwarded back to the connected TCP client.
-  The ESP32 does not parse or process the Modbus protocol; it only acts as a bridge.
-  The external MCU connected to the UART port must implement the Modbus RTU/ASCII server logic.
-  Make sure the ESP32 is connected to a WiFi network (Station mode) or has an active SoftAP before starting the bridge.

Example
^^^^^^^

::

    // Start Modbus TCP bridge on default port 502
    AT+MODBUSTCP=1,502,60

    // Query bridge status
    AT+MODBUSTCP?

    // Stop Modbus TCP bridge
    AT+MODBUSTCP=0

Typical Usage Scenario
^^^^^^^^^^^^^^^^^^^^^^

1. Configure ESP32 as SoftAP or connect to a WiFi network:

   ::

       AT+CWMODE=2
       AT+CWSAP="ESP32_AP","12345678",5,3

2. Start the Modbus TCP bridge:

   ::

       AT+MODBUSTCP=1,502,60

3. Connect a Modbus TCP master (e.g., Modbus Poll, SCADA) to ``192.168.4.1:502``.

4. The Modbus TCP master sends queries, which are forwarded to the MCU via UART.

5. The MCU processes the Modbus requests and sends responses back via UART.

6. ESP32 forwards the MCU responses to the Modbus TCP master.

URC Messages
^^^^^^^^^^^^

The following Unsolicited Result Codes (URCs) may be reported:

- ``+MODBUSTCP:LISTENING``: TCP server started and waiting for client connections.
- ``+MODBUSTCP:CONNECTED``: A Modbus TCP client has connected.
- ``+MODBUSTCP:DISCONNECTED``: The connected client has disconnected.
- ``+MODBUSTCP:STOPPED``: The Modbus TCP bridge has been stopped.
