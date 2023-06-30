#include "runner.h"

int test(LIBSSH2_SESSION *session)
{
#if LIBSSH2_RSA_SHA1
    /* set in Dockerfile */
    return test_auth_pubkey(session, 0,
                            "libssh2",
                            "libssh2",
                            "key_rsa_encrypted.pub",
                            "key_rsa_encrypted");
#else
    (void)session;
    return 0;
#endif
}
