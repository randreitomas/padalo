import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPhp(value: string | number) {
  return new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(Number(value));
}

export function formatDecimal(value: string | number, fractionDigits = 2) {
  return new Intl.NumberFormat("en-PH", {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  }).format(Number(value));
}

export function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-PH", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

export function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("en-PH", {
    day: "numeric",
    month: "short",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export function toMoneyInput(value: string | number) {
  return Number(value).toFixed(2);
}

export function toDateInput(value: string) {
  return value.slice(0, 10);
}

export function toDateTimeLocalInput(value: string) {
  const date = new Date(value);
  const offset = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}
