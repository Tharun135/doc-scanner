# Configuration scenarios

The SIMATIC S7 Connector allows you to add field devices to IED and create data point lists. It supports multiple user access with the following scenarios:

* One user can access SIMATIC S7 Connector on multiple IEDs.<br/>
  But the user cannot access SIMATIC S7 Connector on the same IED in multiple tabs of same browser or multiple browsers.
* Two users can access SIMATIC S7 Connector on two different IEDs simultaneously.<br/>
  When the two users access SIMATIC S7 Connector on the same IED, a message is displayed to the second user that the IED is in use already. Therefore, the second user cannot access SIMATIC S7 Connector.

!!! info "NOTICE"

    When you perform following actions:
    
    * adding, editing, or deleting a data source,
    * adding, editing, importing, or deleting a tag,
    
    you must click **Deploy** to save the changes on the Industrial Edge Runtime of the SIMATIC S7 Connector.
