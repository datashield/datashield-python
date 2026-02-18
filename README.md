# DataSHIELD Interface Python

This DataSHIELD Client Interface is a Python port of the original DataSHIELD Client Interface written in R ([DSI](https://github.com/datashield/DSI)). The provided interface can be implemented for accessing a data repository supporting the DataSHIELD infrastructure: controlled R commands to be executed on the server side are garanteeing that non disclosive information is returned to client side.

## Configuration

The search path for the DataSHIELD configuration file is the following:

1. User general location: `~/.config/datashield/config.yaml`
2. Current project specific location: `./.datashield/config.yaml`

The configurations are merged: any existing entry is replaced by the new one (for instance server names must be unique).

The format of the DataSHIELD configuration file is:

```yaml
servers:
  - name: server1
    url: https://opal-demo.obiba.org
    user: dsuser
    password: P@ssw0rd
  - name: server2
    url: https://opal.example.org
    token: your-access-token-here
    profile: default
  - name: server3
    url: https://study.example.org/opal
    user: dsuser
    password: P@ssw0rd
    profile: custom
    driver: datashield_opal.OpalDriver
```

Each server entry in the list must have:
- `name`: Unique identifier for the server
- `url`: The server URL
- Authentication: Either `user` and `password`, or `token` (recommended)
- `profile`: DataSHIELD profile name (optional, defaults to "default")
- `driver`: Connection driver class name (optional, defaults to "datashield_opal.OpalDriver")