import PageMeta from "../../components/common/PageMeta";
import AuthLayout from "./AuthPageLayout";
import SignUpForm from "../../components/auth/SignUpForm";

export default function SignUp() {
  return (
    <>
      <PageMeta
        title="Crear cuenta | Academix"
        description="Creá tu cuenta en Academix"
      />
      <AuthLayout>
        <SignUpForm />
      </AuthLayout>
    </>
  );
}
