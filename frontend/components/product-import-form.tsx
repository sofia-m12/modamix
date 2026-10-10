"use client";
import { FormEvent, useState } from "react";
export function ProductImportForm() {
  const [message, setMessage] = useState("");
  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setMessage("Your reference item is ready for import. Backend connection comes next."); }
  return <form onSubmit={submit}><label htmlFor="url">Retail product URL</label><input id="url" name="url" type="url" placeholder="https://retailer.com/product" /><textarea name="changes" placeholder="For example: Keep the cropped fit and forest-green color; change to a smaller collar, no logo, under $100." /><button type="submit">Find my match</button>{message && <p aria-live="polite">{message}</p>}</form>;
}
