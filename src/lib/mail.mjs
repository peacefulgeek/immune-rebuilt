/**
 * Contact-form mailer. Master scope §11 / hard rule: Nodemailer only.
 * Falls back gracefully (logs) when SMTP env is missing — no throw.
 */
import nodemailer from "nodemailer";

let transporter = null;

function getTransporter() {
  if (transporter) return transporter;
  const host = process.env.SMTP_HOST;
  const user = process.env.SMTP_USER;
  const pass = process.env.SMTP_PASS;
  const port = parseInt(process.env.SMTP_PORT || "587", 10);
  if (!host || !user || !pass) return null;
  transporter = nodemailer.createTransport({
    host,
    port,
    secure: port === 465,
    auth: { user, pass },
  });
  return transporter;
}

export async function sendContactEmail({ name, email, message, site }) {
  const t = getTransporter();
  const to = process.env.CONTACT_TO || process.env.SMTP_USER;
  if (!t || !to) {
    console.warn("[mail] SMTP not configured; logging only:", { site, name, email, message: String(message).slice(0, 200) });
    return { ok: false, reason: "smtp-not-configured" };
  }
  await t.sendMail({
    from: process.env.SMTP_USER,
    to,
    replyTo: email,
    subject: `[${site}] Contact from ${name}`,
    text: `From: ${name} <${email}>\n\n${message}`,
  });
  return { ok: true };
}
