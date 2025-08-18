# Delete data source

You can delete a data source in the SIMATIC S7 Connector. The **Data Source** table is updated with the updated list of the data sources. You must deploy the project using **Deploy** button to reflect the deleted configuration.

You cannot delete data sources while **deploy project** operation is running.

## Prerequisite

* The Common Connector Configurator must be running
* The SIMATIC S7 Connector must be running.
* At least one data source must be available.

## Procedure

To delete a data source, follow these steps:

1. Launch the SIMATIC S7 Connector application.<br/>
  The Configurator home page is displayed.
1. Select the data sources you want to delete.
1. Click **Delete** in the upper-left corner. <br/>
  A confirmation message is displayed.
1. Click **OK**.<br/>
  The data sources are deleted and removed from the **Data Source** table.<br/>

    !!! info "NOTICE"

        The deleted data is hidden, and it is only removed from the Industrial Edge Runtime after clicking on **Deploy**.
