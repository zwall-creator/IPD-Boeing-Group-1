import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { SUPABASE_PUBLISHABLE_KEY, SUPABASE_URL } from "./supabase-config.js";

const form = document.querySelector("#auth-form");
const formTitle = document.querySelector("#form-title");
const formDescription = document.querySelector("#form-description");
const nameField = document.querySelector("#name-field");
const displayNameInput = document.querySelector("#display-name");
const emailInput = document.querySelector("#email");
const passwordInput = document.querySelector("#password");
const submitButton = document.querySelector("#submit-button");
const modeButton = document.querySelector("#mode-button");
const signOutButton = document.querySelector("#sign-out-button");
const message = document.querySelector("#auth-message");

let isSignUp = false;
let supabase;

function showMessage(text, isError = false) {
  message.textContent = text;
  message.dataset.error = String(isError);
}

function setBusy(isBusy) {
  submitButton.disabled = isBusy;
  modeButton.disabled = isBusy;
  signOutButton.disabled = isBusy;
}

function setSignedIn(user) {
  form.hidden = true;
  modeButton.hidden = true;
  signOutButton.hidden = false;
  showMessage(`Signed in as ${user.email ?? "your account"}.`);
}

function setSignedOut() {
  form.hidden = false;
  modeButton.hidden = false;
  signOutButton.hidden = true;
}

function updateMode() {
  formTitle.textContent = isSignUp ? "Create account" : "Sign in";
  formDescription.textContent = isSignUp
    ? "Create an account with your email and password."
    : "Use your email and password to continue.";
  nameField.hidden = !isSignUp;
  passwordInput.autocomplete = isSignUp ? "new-password" : "current-password";
  submitButton.textContent = isSignUp ? "Create account" : "Sign in";
  modeButton.textContent = isSignUp
    ? "Already have an account? Sign in"
    : "Need an account? Sign up";
}

if (!SUPABASE_URL || !SUPABASE_PUBLISHABLE_KEY) {
  showMessage(
    "Setup required: add your Supabase project URL and publishable key to supabase-config.js.",
    true,
  );
  submitButton.disabled = true;
  modeButton.disabled = true;
} else {
  supabase = createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY);
  supabase.auth.onAuthStateChange((_event, session) => {
    if (session?.user) {
      setSignedIn(session.user);
    } else {
      setSignedOut();
    }
  });
}

modeButton.addEventListener("click", () => {
  isSignUp = !isSignUp;
  showMessage("");
  updateMode();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!supabase) return;

  setBusy(true);
  showMessage("");

  try {
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (isSignUp) {
      const displayName = displayNameInput.value.trim();
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: displayName ? { display_name: displayName } : {},
        },
      });

      if (error) throw error;
      if (data.session) {
        setSignedIn(data.user);
      } else {
        showMessage("Account created. Check your email to confirm your address, then sign in.");
        isSignUp = false;
        updateMode();
      }
    } else {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) throw error;
      setSignedIn(data.user);
    }
  } catch (error) {
    showMessage(error.message || "Authentication failed. Please try again.", true);
  } finally {
    setBusy(false);
  }
});

signOutButton.addEventListener("click", async () => {
  if (!supabase) return;

  setBusy(true);
  try {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    showMessage("You have signed out.");
  } catch (error) {
    showMessage(error.message || "Could not sign out. Please try again.", true);
  } finally {
    setBusy(false);
  }
});

updateMode();
