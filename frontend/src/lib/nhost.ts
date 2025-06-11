import { NhostClient } from '@nhost/react';

const nhost = new NhostClient({
  subdomain: process.env.NEXT_PUBLIC_NHOST_SUBDOMAIN || 'localhost',
  region: process.env.NEXT_PUBLIC_NHOST_REGION || 'us-east-1',
});

export { nhost }; 