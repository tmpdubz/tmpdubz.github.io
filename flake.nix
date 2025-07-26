{
  description = "Pinned Hugo site dev environment with Hugo 0.148.1, Go 1.24, Node.js 24, and Git";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
      in {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.hugo
            pkgs.go_1_24
            pkgs.nodejs_24
            pkgs.git
          ];

          shellHook = ''
            echo "✅ Dev shell with Hugo 0.148.1, Go 1.24, Node 24, Git"
            echo "💡 Run: hugo server"
          '';
        };
      });
}
