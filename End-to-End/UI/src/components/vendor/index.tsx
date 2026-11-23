import React, { useState, useEffect } from "react";
import { getVendorsResponse } from "../../service";
import { VendorResponse } from "../../types";

type Props = {
  isSelected: boolean;
  name: string;
  id: number;
  onClick: (id: number) => void;
};
export const Vendor = ({
  isSelected,
  name,
  id,
  onClick,
}: Props): JSX.Element => {
  const className = isSelected ? "vendor selected-vendor" : "vendor";
  return (
    <div
      className={className}
      onClick={() => {
        onClick(id);
      }}
    >
      {name}
    </div>
  );
};
