To use and configure mailchimp integration
- create account
- get api key
- create list/audience
- generate a random string > 32 chars
- use string above as MAILCHIMP_WEBHOOK_SECRET (set as env variable)
- create webhook using web frontend (include MAILCHIMP_WEBHOOK_SECRET as part of the URL)
    /announce/mailchimp/somescretsauce
