# About

The code in this repo is for the landing page for the U24 Accelerate Basso Study Network Project. It is a simple static site with HTML, JS, and CSS. The CSS is mainly tailwinds classes, and it can be hosted on any HTTP server as its starting point is an index.html file.

## Heritage

This site was built from the free [Dev Portfolio Template](https://jamie-dev-portfolio.netlify.app/) created by [Paul Freeman](https://github.com/PaulleDemon). The Usage information below is unchanged from the original template. It is accurate, but running the npm scripts will likely yield errors.

- Note that the `css/tailwinds-build.css` file does not cover every class in Tailwinds, just the ones that were used in the original template. This means that attempting to use arbitrary tailwinds classes may not work, and you may need to create custom classes to use functionality that is in the rest of Tailwinds that isn't already included.

- You can get around this limitation and use the rest of tailwinds by developing on this project like a NPM project. Run `npm install` to install tailwinds and any other dependencies in `package.json` to get started with that.

## Usage

- This template uses tailwind css every tailwind class are prefixed with `tw-`, to help differentiate
  between tailwind classes and other classes

During development add the following to head tag

```html
<link
  rel="stylesheet"
  href="tailwind-runtime.css"
/><!--replace with path to your tailwind runtime-->
```

During production use

```html
<link
  rel="stylesheet"
  href="tailwind-build.css"
/><!--replace with path to your tailwind build-->
```

To start Tailwind during development use

```html
npm run start:tailwind
```

To create a build file use

```html
npm run build:tailwind
```
