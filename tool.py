import pprint

ls = ["attorney",
      "citizen-auth-frontend",
      "saml",
      "auth",
      "authenticator",
      "matching",
      "matching-adapter",
      "citizen-details",
      "user-details",
      "tax-enrolments",
      "iv-callcredit-proxy",
      "iv-callvalidate-proxy",
      "identity-verification-frontend",
      "identity-verification",
      "dwp-data",
      "child-benefit-data",
      "hmpo-proxy",
      "companies-house-api-proxy",
      "verification-frontend",
      "passcode",
      "passcode-acceptance-tests",
      "passcode-verification",
      "whitelist-campaign-frontend",
      "platform-authentication-acceptance-tests",
      "auth-performance-tests",
      "iv-performance-tests",
      "demo-frontend",
      "auth-login-stub",
      "auth-login-api",
      "identity-verification-stub",
      "matching-stub",
      "iv-test-data",
      "key-store",
      "save4later",
      "sso-frontend",
      "sso",
      "scala-webdriver",
      "platform-analytics",
      "portal-stub",
      "ld-schema",
      "enrolment-exception-list",
      "sos-reporting"]


def dosth():
    for l in sorted(ls):
        print('"%s|" +' % l)


if __name__ == "__main__":
    dosth()
