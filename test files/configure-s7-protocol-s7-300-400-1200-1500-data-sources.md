# Configure S7-Protocol (S7-300-400-1200-1500) data sources

You can configure S7-Protocol (S7-300/400/1200/1500) controller data source in the SIMATIC S7 Connector application. The configurator allows you to configure the S7-Protocol (S7-300/400/1200/1500) communication channel to the SIMATIC PLCs for data acquisition.

## Example Scenario

A Plant Administrator or Industrial Edge Box Operator would like to configure the data acquisition from the S7-Protocol (S7-300/400/1200/1500) controller, and subsequently would like to create value from the acquired data.

## Prerequisite

* The SIMATIC S7 Connector must be running.
* The Common Connector Configurator must be running.

## Procedure

To configure S7-Protocol (S7-300/400/1200/1500) controller data source, follow these steps:

1. Launch the SIMATIC S7 Connector application.<br/>
  The configurator home page is displayed.
1. Click **Add Data Source** in the upper-left corner. <br/>
  The **Add** dialog box is displayed as follows:<br/>
  ![171299003275-d2e1640](../media/171299003275.png)
1. Select the S7-Protocol (S7-300/400/1200/1500) data source type from the **Data Source Type** drop-down.<br/>
  The fields are displayed as follows:<br/>
  ![171299008651-d2e1651](../media/171299008651.png)
1. Complete the following fields:<br/>

    | Field Name | Definition |
    | --- | --- |
    | Name | Defines the name of the data source. It must be unique. |
    | IP Address | Defines the IP address of the S7-Protocol (S7-300/400/1200/1500) controller with the desired data points. |
    | Rack Number | Defines the rack of the S7-Protocol (S7-300/400/1200/1500) controller. The default value is 0. |
    | Slot Number | Defines the slot of the S7-Protocol (S7-300/400/1200/1500) controller. The default value is 1. |
    | PLC Type | Specifies the PLC type. |
    | Full Text Alarms | Enables the full text alarms. This field is displayed when you select **PLC Type** as 300/400.<br/>This checkbox is enabled only when project runtime is not running. |

1. Click **Add**.<br/>
  The data source is added and displayed in the **Data Source** table.
