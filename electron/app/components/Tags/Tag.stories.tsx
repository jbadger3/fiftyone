import React from "react";
import Tag from "./Tag";

export default {
  component: Tag,
  title: "Tag",
};

export const standard = () => <Tag name="tag"></Tag>;

export const color = () => <Tag name="tag" color="red"></Tag>;
