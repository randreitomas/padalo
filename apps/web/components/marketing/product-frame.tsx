import Image from "next/image";

import { cn } from "@/lib/utils";

type ProductFrameProps = {
  alt: string;
  aspectClassName?: string;
  className?: string;
  imageClassName?: string;
  label?: string;
  priority?: boolean;
  sizes: string;
  src: string;
};

export function ProductFrame({
  alt,
  aspectClassName,
  className,
  imageClassName,
  label = "Padalo product preview",
  priority = false,
  sizes,
  src,
}: ProductFrameProps) {
  return (
    <figure
      className={cn(
        "product-frame overflow-hidden rounded-lg border border-[#d6dcda] bg-white shadow-[0_24px_70px_rgba(20,35,32,0.12)]",
        className,
      )}
    >
      <div
        aria-hidden="true"
        className="flex h-10 items-center gap-1.5 border-b border-[#e2e7e4] bg-[#f8f9f8] px-4"
      >
        <span className="size-2 rounded-full bg-[#d5ddda]" />
        <span className="size-2 rounded-full bg-[#d5ddda]" />
        <span className="size-2 rounded-full bg-[#d5ddda]" />
        <span className="ml-3 truncate text-[11px] font-medium text-[#71807b]">{label}</span>
      </div>
      <div className={cn("relative aspect-[16/10] overflow-hidden bg-[#edf1ef]", aspectClassName)}>
        <Image
          alt={alt}
          className={cn("product-frame-image object-cover", imageClassName)}
          fill
          priority={priority}
          sizes={sizes}
          src={src}
        />
      </div>
    </figure>
  );
}
