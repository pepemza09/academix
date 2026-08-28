import { HelmetProvider, Helmet } from "react-helmet-async";

const APP_NAME = "Academix";

const PageMeta = ({
  title: _title,
  description,
}: {
  title?: string;
  description: string;
}) => (
  <Helmet>
    <title>{APP_NAME}</title>
    <meta name="description" content={description} />
  </Helmet>
);

export const AppWrapper = ({ children }: { children: React.ReactNode }) => (
  <HelmetProvider>{children}</HelmetProvider>
);

export default PageMeta;
