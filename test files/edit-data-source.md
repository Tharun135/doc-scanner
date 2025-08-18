# Edit data source

You can edit a data source in the SIMATIC S7 Connector and update the required details. The updated details are configured for the data source.

## Prerequisite

* The Common Connector Configurator must be running.
* The SIMATIC S7 Connector must be running.
* A data source must be available.

## Procedure

To edit a data source, follow these steps:

1. Launch the SIMATIC S7 Connector application.<br/>
  The Configurator home page is displayed.
1. Click ![171304060555-d2e1941](../media/171304060555.png) under the **Actions** column of the data source that you want to edit.<br/>
  The **Edit Data Source** dialog box is displayed.
1. Modify the relevant details.<br/>

    !!! info "NOTICE"

        You cannot edit the **Connection Name** and **IP Address** for a data source once it is at Industrial Edge Runtime (project deployed and started).
        
        When you  modify a deployed connection, then its deployed state is changed to partially deployed state.

1. Click **Save**.<br/>
  The data source is modified and displayed in the **Data Source** table.
