# PulseCheck — Python + DevOps + AWS Project Plan

A website uptime monitor built in Flask, containerized with Docker, deployed to AWS
via Terraform, with a full CI/CD pipeline on GitHub Actions.

**Target: Tata Power GET-CS/IT placement prep**
**Timeline: 2-3 weeks**

---

## Why this project

Maps directly onto the JD's key skills:

| JD requirement | How this project demonstrates it |
|---|---|
| Cloud Infrastructure Management | EC2 provisioning, VPC, security groups |
| Infrastructure as Code (IaC) | Terraform for all AWS resources |
| Automation and Scripting | GitHub Actions CI/CD pipeline |
| Security Management | IAM least-privilege user, security group rules |
| Services Management | RDS (database), CloudWatch (monitoring/alerts) |
| Version control (Git) | Full repo history, branches, PRs |
| Agile development | Track work as sprints in GitHub Projects |
| Programming (Python) | Entire app logic |

**Scope discipline:** No Kubernetes, no frontend framework, no microservices.
A simple project you can explain end-to-end beats a complex one you can't.

---

## Architecture

```
Developer push --> GitHub Actions (test, build, push image) --> Amazon ECR
                          |
                          v
                   Terraform apply
                          |
                          v
        AWS: EC2 (runs app) --> RDS Postgres (check history)
                 |
                 v
             CloudWatch (monitoring/alarms)
                 |
                 v
           Target URLs (sites being monitored)
```

---

## Phase 1 — Core Application (Days 1-4)

### Day 1-2: Flask app core
- [ ] Set up project structure:
  ```
  pulsecheck/
    app/
      __init__.py
      routes.py
      checker.py
      models.py
      templates/
        dashboard.html
    tests/
    requirements.txt
    Dockerfile
    docker-compose.yml
  ```
- [ ] Build the checker logic: given a list of URLs, ping each with `requests`,
      record status code + response time
- [ ] Use `threading` or `APScheduler` to run checks on a schedule (e.g. every 5 min)
- [ ] Store results in SQLite locally (swap for Postgres later)
- [ ] Basic Flask routes: `/` (dashboard), `/api/status` (JSON), `/add-url`

### Day 3: Dashboard
- [ ] Jinja2 template showing each monitored URL: current status, last response
      time, uptime % over last 24h
- [ ] Simple styling (Bootstrap CDN is fine — don't over-invest here)

### Day 4: Dockerize
- [ ] Write a `Dockerfile` (multi-stage if you want extra points: builder +
      slim runtime image)
- [ ] Write `docker-compose.yml` for local dev (app + Postgres)
- [ ] Verify: `docker compose up` works end-to-end locally

**Checkpoint:** App runs locally in Docker, dashboard shows live status of 3-5 URLs.

---

## Phase 2 — Cloud Infrastructure (Days 5-9)

### Day 5: AWS account + IAM
- [ ] Create AWS account, enable free tier alerts/budget (set a $5 budget alarm)
- [ ] Create an IAM user for Terraform (NOT root) with least-privilege policy
      (EC2, RDS, ECR, CloudWatch access only)
- [ ] Install AWS CLI, configure with `aws configure`
- [ ] Install Terraform locally

### Day 6-7: Terraform — networking + compute
- [ ] `main.tf` — provider block, backend config (local state is fine to start)
- [ ] `vpc.tf` — VPC, public subnet, internet gateway, route table
- [ ] `security_groups.tf` — allow inbound 22 (SSH, your IP only), 80/5000
      (app), outbound all
- [ ] `ec2.tf` — EC2 instance (t2.micro / t3.micro, free tier), key pair,
      user-data script to install Docker on boot
- [ ] `terraform init && terraform plan` — review before applying

### Day 8: Terraform — database
- [ ] `rds.tf` — PostgreSQL instance (db.t3.micro, free tier), in a private
      subnet if you want to go further, otherwise public with a strict SG
- [ ] Store DB credentials in AWS Secrets Manager or at minimum as Terraform
      variables (never hardcode — mention this in interviews as a security
      awareness point)
- [ ] Update Flask app config to read DB connection string from environment
      variable

### Day 9: Apply + verify
- [ ] `terraform apply`
- [ ] SSH into EC2, manually pull and run the Docker image once to confirm
      everything connects (app <-> RDS)
- [ ] Confirm dashboard is reachable via EC2 public IP

**Checkpoint:** Infrastructure is live on AWS, provisioned entirely through
Terraform, app manually deployed and working.

---

## Phase 3 — CI/CD Pipeline (Days 10-14)

### Day 10: Repo structure + GitHub setup
- [ ] Push code to GitHub (structure: `app/`, `terraform/`, `.github/workflows/`)
- [ ] Add `.gitignore` (exclude `.tfstate`, `.env`, `__pycache__`)
- [ ] Write a clear README skeleton (fill in fully at the end)

### Day 11-12: CI (Continuous Integration)
- [ ] `.github/workflows/ci.yml`:
  - Trigger on push/PR to `main`
  - Install dependencies
  - Run `pytest`
  - Run `flake8` or `black --check` for linting
- [ ] Make sure CI fails loudly on a broken test (test this deliberately once)

### Day 13-14: CD (Continuous Deployment)
- [ ] Create an ECR repository (via Terraform, `ecr.tf`)
- [ ] Extend the workflow: on merge to `main`, build Docker image, tag with
      commit SHA, push to ECR
- [ ] Deploy step: SSH into EC2 (using a GitHub Actions SSH action) to pull
      the new image and restart the container — OR use an EC2 user-data /
      systemd approach that polls ECR
- [ ] Add CloudWatch alarm: EC2 CPU > 80%, and/or a custom metric for "URL
      down" events from your app

**Checkpoint:** A `git push` to main automatically tests, builds, and
redeploys the app to AWS with no manual steps.

---

## Phase 4 — Polish (Days 15-18)

### Day 15: Tests
- [ ] Unit tests for the checker logic (mock `requests` responses — up, down,
      timeout cases)
- [ ] At least one integration test for a Flask route

### Day 16-17: Documentation
- [ ] Full README: problem statement, architecture diagram, tech stack, how
      to run locally, how to deploy, screenshots of the dashboard
- [ ] Include the architecture diagram (recreate the one from this plan, or
      draw it in draw.io / Excalidraw)
- [ ] Document any trade-offs you made and why (this is gold for interviews)

### Day 18: Cost cleanup
- [ ] `terraform destroy` when not actively demoing, to stay within free tier
- [ ] Note the exact `terraform apply` / `destroy` commands in README so you
      can spin it back up before an interview demo

---

## Phase 5 — Interview Prep (Days 19-21)

### Talking points to rehearse out loud
- [ ] "Walk me through your project" — 60-90 second version
- [ ] Why Terraform over manual console setup? (repeatability, version
      control, disaster recovery)
- [ ] Why Docker? (consistency across dev/prod, easy redeployment)
- [ ] What security measures did you implement? (least-privilege IAM,
      security groups scoped to specific ports/IPs, secrets not hardcoded)
- [ ] What would you do differently at scale? (auto-scaling group instead of
      single EC2, RDS Multi-AZ, private subnets + NAT gateway, secrets
      manager instead of env vars)
- [ ] What broke during the build, and how did you debug it? (have a real
      story ready — this is often asked)

### Buffer
- [ ] Reserve these days for whatever inevitably goes wrong in Phases 2-3
      (most common: security group misconfiguration, IAM permission errors,
      Docker networking issues)

---

## Quick reference: minimum viable version

If you fall behind schedule, this is the floor — do not cut below this:
1. Flask app running in Docker locally ✅
2. EC2 + RDS provisioned via Terraform (even if deployment to EC2 is manual) ✅
3. GitHub Actions running tests on push ✅
4. A README that explains the architecture clearly ✅

Being able to **explain every decision** in a smaller working project beats
having a bigger broken one.
