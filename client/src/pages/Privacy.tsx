export default function Privacy() {
  return (
    <div className="container py-14 md:py-20 max-w-3xl">
      <p className="text-xs uppercase tracking-[.18em] text-[oklch(0.45_0.075_150)] mb-2">How we handle your data</p>
      <h1 className="text-3xl md:text-5xl font-semibold tracking-tight">Privacy</h1>
      <div className="ar-prose mt-8">
        <p>
          Immune Rebuilt is a small editorial site. We collect as little data as we can get away with.
        </p>
        <h2>What we collect</h2>
        <p>
          Standard server logs (IP, user agent, page requested, timestamp). Privacy-friendly,
          aggregate analytics for understanding which essays land. No third-party advertising trackers.
          No retargeting pixels.
        </p>
        <h2>Cookies</h2>
        <p>
          We set no marketing cookies. The site uses a session cookie only when you submit
          the contact form, to keep the form from being abused.
        </p>
        <h2>Email</h2>
        <p>
          The contact form is delivered by email through our own server (Nodemailer) ,  no
          third-party email marketing service has access to messages you send us. We do not have
          a mailing list at this time.
        </p>
        <h2>Affiliate links</h2>
        <p>
          Outbound Amazon links carry our associate tag (<code>spankyspinola-20</code>). Amazon
          tracks those visits per their own policies. See our{" "}
          <a href="/disclosures">disclosures</a> for the full picture.
        </p>
        <h2>Children</h2>
        <p>
          The site is for adults seeking information about chronic autoimmune conditions and
          recovery. We do not knowingly collect data from anyone under 16.
        </p>
        <h2>Contact</h2>
        <p>
          Questions? Use the <a href="/contact">contact form</a>. We read everything that comes in.
        </p>
      </div>
    </div>
  );
}
