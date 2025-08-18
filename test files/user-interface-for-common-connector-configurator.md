# User Interface for Common Connector Configurator

When you launch SIMATIC S7 Connector application, the home page is displayed as follows:

![169665550731-d2e1240](../media/169665550731.png)

!!! info "NOTICE"

    A data source added for better understanding. For more information, refer [Configuring data sources](../configuration-using-common-connector-configurator/configuring-data-sources.md).

## UI elements

The following table lists the different UI elements in the **Configure Data Source** page:

| Symbol | Description |
| --- | --- |
| ① Add Data Source | Enables to add a new data source. |
| ② Connection status | Displays the connection status of PLC. |
| ③ Connection/Tag deployed status | Displays the status of Tag deployment. |
| ④ Delete tab | Enables to delete the data source and data points. |
| ⑤ Connection status ofBus adapter | Displays the connection status of the adapter. |
| ⑥ Data Source table | Displays the data source connections and data points and their information as follows:<ul><li>**Name**: Displays the name of the data point. You can use ![148253371275-d2e1317](../media/148253371275.png) to align the data point name. By default, the data point name is left aligned.</li><li>**Comments**: Displays the given comments.</li><li>**Address**: Displays the address of the data point.</li><li>**Data Type**: Displays the data point type.</li><li>**Acquisition Cycle**: Displays the acquisition cycle with which the data is sent to the Databus.</li><li>**Acquisition Mode**: Displays the acquisition mode with which the data is sent to the Databus.</li><li>**Access Mode**: Displays the access permission.</li><li>**Actions**: Displays the **Edit Data Source**, **Add Tags**, **Import Tags**, and **Browse** options. For more information, refer [Configuring tags/data points](../configuring-tags-data-points/add-tags.md).</li></ul> |
| ⑦ Deploy tab | Enables to deploy the project. If you close the SIMATIC S7 Connector, then all the unsaved configurations are lost. The **Deploy** button saves the configuration on the Industrial Edge Runtime of the SIMATIC S7 Connector. |
| ⑧ Import/Export tab | Enable to import and export the configuration. For more information, refer [Import/Export configuration](../managing-project/import-export-configuration.md). |
| ⑨ Settings tab | Enables to perform the following tasks:<ol><li>You can edit Databus service name.</li><li>You can specify SIMATIC S7 Connector user credentials which you define in Databus Configurator.</li><li>You can specify payload version of the SIMATIC S7 Connector.</li><li>You can specify browse timeout. For more information, refer [Configure settings](../managing-project/configure-settings.md).</li></ol> |

## Connection status

The following table shows the connection status of Bus adaptor connection with tag data/metadata and alarm data MQtt clients:

| | |
| --- | --- |
| **Symbol** | **Status** |
| ![171297434635-d2e1431](../media/171297434635.png) |  <br/>Tagdata, metadata and alarmdata client is connected to bus adaptor. |
| ![171297443211-d2e1440](../media/171297443211.png) |  <br/>At least one of the tag data, metadata, and alarm data client is disconnected from bus adaptor. |
| ![171297464587-d2e1449](../media/171297464587.png) |  <br/>No connection state with bus adaptor. This is a warning. |

The following table shows the connection status of the PLCs:

| | |
| --- | --- |
| **Symbol** | **Status** |
| ![171297473163-d2e1472](../media/171297473163.png) | The connection is good and established. |
| ![171297507339-d2e1479](../media/171297507339.png) | The connection is bad and not established. |
| ![171297592715-d2e1486](../media/171297592715.png) | No state. This is the default value if project is not running or if connection is new. |

The following table shows the deployed status of Connection and Tag:

| Symbol | Status |
| --- | --- |
| ![171297225483-d2e1508](../media/171297225483.png) | Fully deployed - Connection/Tag is Fully deployed with no modification/errors. |
| ![171297426059-d2e1515](../media/171297426059.png) | Partially deployed - Connection/Tag is Partially deployed – Either deployed Tag/Connection was modified or deploy failed. |
| ![169665669131-d2e1522](../media/169665669131.png) | Not deployed – Connection/Tag is not deployed to runtime. |

!!! info "NOTICE"

    * When connection and tag deployment are successful, state is marked with full deployment.
    * When tag deployment fails, the state is marked with no deployment.
    * When a tag or connection is modified, the state is marked as partial deployment.
