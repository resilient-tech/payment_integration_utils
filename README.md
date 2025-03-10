<div align="center">

# Payment Integration Utils

This app provides core utilities to build bank integrations in ERPNext. It includes common roles, workflows, custom fields, and other helpers. Use it as a base for secure online payment handling with minimal setup.

</div>

## ✨ Features

- **Common Payment Authorization Roles**: Predefined roles for secure payment handling.  
- **Payment Authentication**: Built-in support for two-factor authentication (2FA).  
- **Reusable Workflows**: Ready-to-use workflows for bank payments.  
- **Custom Fields**: Flexible fields to support various integration needs.  
- **Utilities**: Tools to streamline online payment processes.  
- **Bulk Payments Action**: Efficiently handle bulk payments.  

## 📦 Installation

### Prerequisites

- [ERPNext](https://github.com/frappe/erpnext) Version-15 or above.

### Installation Methods

<details>
<summary>☁️ Frappe Cloud</summary><br>

1. Sign up for a [Frappe Cloud](https://frappecloud.com/dashboard/signup?referrer=99df7a8f) free trial.  
2. Create a new site with Frappe Version-15 or above.  
3. Install ERPNext and **Payment Integration Utils** from the Apps Marketplace.  

</details>

<details>
<summary>🐳 Docker</summary><br>

Use [this guide](https://github.com/frappe/frappe_docker/blob/main/docs/custom-apps.md) to deploy **Payment Integration Utils** by building your custom image.  

Sample Apps JSON:  

```shell
export APPS_JSON='[
  {
    "url": "https://github.com/frappe/erpnext",
    "branch": "version-15"
  },
  {
    "url": "https://github.com/resilient-tech/payment_integration_utils",
    "branch": "version-15"
  }
]'

export APPS_JSON_BASE64=$(echo ${APPS_JSON} | base64 -w 0)
```

</details>

<details>
<summary>⌨️ Manual</summary><br>

1. Set up a Frappe site using [this guide](https://frappeframework.com/docs/v14/user/en/installation/).  
2. Install the app using Bench CLI:  

```sh
bench get-app https://github.com/resilient-tech/payment_integration_utils.git --branch version-15
```

- Install the app on your site:  

```sh
bench --site SITE_NAME install-app payment_integration_utils
```

</details>

## 🛠️ Usage

Extend or override existing payment logic to suit your bank’s requirements.  

For an example implementation, see [RazorpayX Integration](https://github.com/resilient-tech/razorpayx-integration).  

## 📚 Documentation

Read the full documentation [here](https://github.com/resilient-tech/payment_integration_utils/blob/version-15/docs).  

## 🤝 Contributing

- [Issue Guidelines](https://github.com/frappe/erpnext/wiki/Issue-Guidelines)  
- [Pull Request Requirements](https://github.com/frappe/erpnext/wiki/Contribution-Guidelines)  

## 📜 License

[GNU General Public License (v3)](https://github.com/resilient-tech/payment-integration-utils/blob/version-15/license.txt)  
