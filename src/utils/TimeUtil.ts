export class TimeUtil {
  // util class for date formating
  static format(date: Date, format: string): string {
    if (format === "ISO") return date.toISOString();
    if (format === "UTC") return date.toUTCString();
    if (format === "LOCAL") return date.toLocaleString();

    const pad = (n: number, width = 2) => n.toString().padStart(width, "0");

    const tokens: Record<string, string> = {
      YYYY: pad(date.getFullYear(), 4),
      MM: pad(date.getMonth() + 1),
      DD: pad(date.getDate()),
      HH: pad(date.getHours()),
      mm: pad(date.getMinutes()),
      ss: pad(date.getSeconds()),
      SSS: pad(date.getMilliseconds(), 3),
    };

    return format.replace(/YYYY|MM|DD|HH|mm|ss|SSS/g, (match) => tokens[match] || match);
  }
}
