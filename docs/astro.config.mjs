// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import markdoc from "@astrojs/markdoc";

import node from "@astrojs/node";

// https://astro.build/config
export default defineConfig({
  site: "https://python.socra.com",
  integrations: [
    markdoc(),
    starlight({
      title: "socra Python",
      social: {
        github: "https://github.com/socra/socra-python",
        "x.com": "https://x.com/socra_ai",
      },
      customCss: [
        // Relative path to your custom CSS file
        "./src/styles/custom.css",
      ],
      sidebar: [
        "introduction",
        // {
        //   label: "Introduction",
        //   items: [
        //     // Each item here is one entry in the navigation menu.
        //     // { label: "Example Guide", slug: "guides/example" },
        //   ],
        // },
        {
          label: "Guides",
          items: [
            // Each item here is one entry in the navigation menu.
            { label: "Example Guide", slug: "guides/example" },
          ],
        },
        {
          label: "Reference",
          autogenerate: { directory: "reference" },
        },
      ],
    }),
  ],

  output: "server",

  adapter: node({
    mode: "standalone",
  }),
});
