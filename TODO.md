TODOs
=====


1. Fix authorisation for the $connect websocket. YAML won't deploy authoriser. - DONE
2. Write Test cases
3. Architecture diagram
4. Plugin architecture for generic UC platform / Genesys/AXP/Infinith/Zoom
5. Improve error handling for production
6. Add front end to deployment script
7. InboundDispatcher should read from a DynamoDB company config table
8. The company config table should store the AWS secret names that have the cc credentials
9. Encrypt the query strings with HMAC, short token expiry and origin identification    
10. Whitelisting / VPC
11. SSO/Authentication!!
12. Review Deployer permissions
13. Re-architect inbound processor to split the intent processing out
14. Better error handling / inform user when an error occurs
15. Add a "typing" route to the web socket
16. Add Dead Letter queues