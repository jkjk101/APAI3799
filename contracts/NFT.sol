// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts@5.0.0/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts@5.0.0/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts@5.0.0/token/ERC721/extensions/ERC721Burnable.sol";
import "@openzeppelin/contracts@5.0.0/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts@5.0.0/token/common/ERC2981.sol";
import "@openzeppelin/contracts@5.0.0/access/Ownable.sol";

contract NFT is ERC721, ERC721URIStorage, ERC721Burnable, ERC721Enumerable, ERC2981, Ownable {
    constructor(address initialOwner, string memory name, string memory symbol)
        ERC721(name, symbol)
        Ownable(initialOwner)
    {}

    function safeMint(address to, uint256 tokenId, string memory uri, uint96 royaltyPercentage)
        public
        onlyOwner
    {
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        _setTokenRoyalty(tokenId, to, royaltyPercentage*100);
    }

    function safeMintAndStartSale(uint256 N,  string memory uri, uint256 price, uint96 royaltyPercentage)
        public
        onlyOwner
    {   
        uint256 total = totalSupply();
        for (uint i = 0; i < N; i++) {
            uint256 tokenId = total + i + 1;
            _safeMint(owner(), tokenId);
            _setTokenURI(tokenId, uri);
            _setTokenRoyalty(tokenId, owner(), royaltyPercentage*100);
            startSale(tokenId, price);
        }
    }

    struct Sale {
        uint256 price;
    }

    mapping(uint256 => Sale) public sales;

    function startSale(uint256 tokenId, uint256 price) public {
        require(sales[tokenId].price == 0, "NFT is already for sale");
        require(ownerOf(tokenId) == msg.sender, "Only the owner can start a sale");

        sales[tokenId] = Sale(price);
    }

    function cancelSale(uint256 tokenId) public {
        require(sales[tokenId].price > 0, "NFT is not currently for sale");
        require(ownerOf(tokenId) == msg.sender, "Only the owner can cancel the sale");

        delete sales[tokenId];
    }

    function buyNFT(uint256 tokenId) public payable {
        require(msg.sender != ownerOf(tokenId), "You already own this NFT");
        require(sales[tokenId].price > 0, "NFT is not currently for sale");
        require(msg.value >= sales[tokenId].price, "Insufficient payment");

        address seller = ownerOf(tokenId);
        address buyer = msg.sender;
        uint256 salePrice = sales[tokenId].price;
        (address creator, uint256 royaltyAmount) = royaltyInfo(tokenId, salePrice);

        // Transfer ownership of the token to the buyer
        _transfer(seller, buyer, tokenId);

        // Delete the sale
        delete sales[tokenId];

        // Transfer royalty to the creator
        if (royaltyAmount > 0) {
            payable(creator).transfer(royaltyAmount);
        }

        // Transfer funds to the seller
        payable(seller).transfer(salePrice - royaltyAmount);

        // Refund excess payment to the buyer
        if (msg.value > salePrice) {
            payable(buyer).transfer(msg.value - salePrice);
        }

    }

    // The following functions are overrides required by Solidity.

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage, ERC721Enumerable, ERC2981)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    function _update(address to, uint256 tokenId, address auth) 
        internal 
        virtual 
        override (ERC721, ERC721Enumerable)
        returns (address) 
    {
        return super._update(to, tokenId, auth);
    }

    function _increaseBalance(address account, uint128 amount) 
        internal 
        virtual 
        override (ERC721, ERC721Enumerable)
    {
        super._increaseBalance(account, amount);
    }

}