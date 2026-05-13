# Simple self-hosting with docker compose, caddy, borg and git

**What is this?** An easy-to-maintain server setup with decent security, decent reliability (backups, monitoring) and the whole thing is versioned in git and your password manager. Tradeoffs are disclaimed below.

---

# Requirements

- a VPS server with linux and [docker compose installed](https://docs.docker.com/compose/install/)
- a storage server that will contain your backups, [compatible with borg](https://torsion.org/borgmatic/reference/configuration/repositories/): sftp, ssh, s3, ...
- a domain name
- a git remote to version your infrastructure (not hosted on this server in case it goes down...)

---

# Services

### Backbone services

- Caddy **reverse proxy** that handles HTTPS transparently.
- **Backup** powered by borgmatic
- **Monitoring** (ad-hoc python script) that runs hourly and emails you if:
  - an endpoint is unreachable or non-200
  - your load average is too high
  - your disk space is too low
  - no successful backup has completed in the last day

### Example services included in this example (adapt to your needs)

- Nextcloud (alternative to Google Drive or iCloud)
- [Immich](https://immich.app/), alternative to Google Photos or iCloud Photos.
- BitTorrent with a Web UI, that downloads through a VPN
- [Jellyfin](https://jellyfin.org/) (media server) connected to the BitTorrent downloads folder

### Adding services

1. add to `docker-compose.yml` and expose only to localhost (`127.0.0.1:port:port`).
2. everything in `./data` is backed up by default. If you want to exclude it from backups, change `borgmatic/config.yml`. If it's a database, use the appropriate borgmatic sections.
3. set up a subdomain with an entry `A {public IP address of your server}`
4. add to `caddy/Caddyfile`
5. start the service `docker compose up -d` and rebuild Caddy `docker compose up -d --build caddy`

---

# Setup

### Security

- Use a LTS, "package-conservative" distro like debian to minimize exposure to new CVEs. Everything runs in docker anyway.
- ❗Check that **no** user on your server has password authentication on. 
- ❗Set up [automatic security upgrades](https://wiki.debian.org/PeriodicUpdates) for your distro.
- Use unique passwords to authenticate to the various services you self-host.
- Regularily update your images, `docker compose pull [service]` but beware of breaking changes.

### Secrets

Initialize a `.env` file and keep it in sync with your password manager manually.

```
IMMICH_APP_DB_PASSWORD="(set to a random password)"
BORGMATIC_KEY="(set to a random password)"
# whatever else you need...
```

### Backups

- Edit `borgmatic/config.yml` to set the backup destination. I use a Hetzner box (cheap and includes snapshots).
- Add a private key that can access your backup destination in `borgmatic/ssh/box_key`. It is gitignored.

### Versioning your infrastructure

This repo is designed to be versioned in git. Secrets and the data folder are gitignored. 

- Secrets: .env goes in your password manager.
- Data: borgmatic backs it up.

Do not add your github/gitlab ssh key to your server! Use a key that has only access to this repo. See appendix

### Healthcheck

Update `docker-compose.yml`'s `EMAIL_{FROM,TO}` envs. Update `healthcheck/config.toml`.

Adapt the python script to your needs!

---

# Disclaimers

### Security

This setup exposes various services to the internet. 

Some might argue it's better to access your services through a VPN, but this is a convenience trade-off. 

If any service has a remote code execution vulnerability and you do not patch it, your server might get compromised. 

I am personally OK with this tradeoff and do not keep anything sensitive on the server / use a separate server that does not expose stuff on the internet for sentitive projects.

If this is properly set up, disaster recovery is simple: git clone and restore from borg.

### Data Loss Prevention

This setup uses "push" backups (the server containing the data pushes to the backup server). 
If your server is compromised, attackers can also damage the backups. 
The preferred setup is "pull" backups where an external backup server connects to your server and, well, pulls it.

---

# Appendix

### Create a SSH key for only one repo on Github

1 - create a ssh key pair  
2 - set up a host in `.ssh/config`

```
Host infra
  HostName github.com
  User git
  IdentityFile ~/infra/id_infra
```
3 - on Github web, go to repo settings and add the public key under "deployment key"
4 - clone with hostname in ssh-config (`git clone git@infra/infra.git`)

---

# Roadmap

- [ ] pin images and add hash check
- [ ] set up rate limiting in Caddy (plugin already included in `caddy/Dockerfile`)
- [ ] envs are all over the place and should be centralized. healthcheck should not need rebuilding everytime the config changes.
