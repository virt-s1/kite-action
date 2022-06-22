# kite-action v2

**kite CI and self-hosted runner auto-scaling**

## Github self-hosted action runner auto-scaling diagram

![kite CI diagram](./kite-action-v2.png)

## Create secret

    $ oc create secret generic openstack-cerdential --from-file=clouds.yaml=~/.config/openstack/clouds.yaml
    $ oc create secret generic gcp-sa-file --from-file=gcp_service_account.json=gcp_service_account.json
